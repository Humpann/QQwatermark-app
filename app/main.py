"""
FastAPI Main Application and API Routers.
"""
import os
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
    version="1.0.0"
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

# Static Files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
