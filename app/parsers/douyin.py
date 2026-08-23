"""
Douyin (抖音) parser supporting 4K Videos, HD Image Albums, Live Photos, and Music.
"""
import re
import json
import urllib.parse
from typing import Optional, List, Dict, Any
import httpx

from app.parsers.base import (
    BaseParser, ParseResult, MediaQuality, LivePhotoItem,
    AuthorInfo, Statistics, get_random_ua
)

class DouyinParser(BaseParser):
    platform_id = "douyin"
    platform_name = "抖音"

    DOUYIN_URL_PATTERN = re.compile(
        r'https?://(?:www\.|v\.|ies\.)?douyin\.com/[^\s\u4e00-\u9fa5]+'
    )

    def match(self, text: str) -> bool:
        return bool(self.DOUYIN_URL_PATTERN.search(text)) or "douyin.com" in text or "iesdouyin.com" in text

    async def parse(self, text_or_url: str) -> ParseResult:
        raw_url = self.extract_url(text_or_url)
        if not raw_url:
            return ParseResult(
                success=False,
                error_message="未在输入中检测到有效的抖音链接",
                platform=self.platform_id,
                platform_name=self.platform_name,
                original_url=text_or_url
            )

        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15.0) as client:
            try:
                # 1. Follow redirect to obtain actual final URL & Aweme ID
                resp = await client.get(raw_url)
                final_url = str(resp.url)
                
                # Extract aweme_id from URL
                aweme_id = self._extract_aweme_id(final_url)
                if not aweme_id:
                    # Try extracting from HTML content or response text
                    aweme_id = self._extract_aweme_id_from_html(resp.text)
                
                if not aweme_id:
                    # Match digits in URL as fallback
                    match_id = re.search(r'/(?:video|note|share/video|share/note)/(\d+)', final_url)
                    if match_id:
                        aweme_id = match_id.group(1)

                if not aweme_id:
                    return ParseResult(
                        success=False,
                        error_message=f"无法从重定向链接获取作品ID: {final_url}",
                        platform=self.platform_id,
                        platform_name=self.platform_name,
                        original_url=raw_url
                    )

                # 2. Fetch data from Douyin API endpoints
                data = await self._fetch_douyin_data(client, aweme_id)
                if not data:
                    return ParseResult(
                        success=False,
                        error_message="获取抖音作品详情失败，可能该内容已被删除或受权限保护",
                        platform=self.platform_id,
                        platform_name=self.platform_name,
                        original_url=raw_url
                    )

                return self._format_result(data, raw_url)

            except Exception as e:
                return ParseResult(
                    success=False,
                    error_message=f"解析抖音内容时发生错误: {str(e)}",
                    platform=self.platform_id,
                    platform_name=self.platform_name,
                    original_url=raw_url
                )

    def _extract_aweme_id(self, url: str) -> Optional[str]:
        patterns = [
            r'/(?:video|note|slides|share/video|share/note|share/slides)/(\d+)',
            r'modal_id=(\d+)',
            r'item_ids=(\d+)',
            r'itemId=(\d+)',
            r'aweme_id=(\d+)',
            r'/(\d{15,})',
            r'(\d{18,20})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _extract_aweme_id_from_html(self, html: str) -> Optional[str]:
        match = re.search(r'awemeId[\'\"]?\s*:\s*[\'\"]?(\d+)', html)
        if match:
            return match.group(1)
        match2 = re.search(r'\"aweme_id\"\s*:\s*\"(\d+)\"', html)
        if match2:
            return match2.group(1)
        return None

    async def _fetch_douyin_data(self, client: httpx.AsyncClient, aweme_id: str) -> Optional[Dict[str, Any]]:
        # API 1: Feed Direct API (100% stable, no WAF / cookie required)
        feed_api_url = f"https://aweme.snssdk.com/aweme/v1/feed/?aweme_id={aweme_id}&aid=1128"
        feed_headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            "Accept": "application/json, text/plain, */*",
        }
        try:
            resp = await client.get(feed_api_url, headers=feed_headers, timeout=8.0)
            if resp.status_code == 200:
                res_json = resp.json()
                items = res_json.get("aweme_list", [])
                if items and len(items) > 0:
                    for it in items:
                        if str(it.get("aweme_id")) == str(aweme_id):
                            return it
                    return items[0]
        except Exception:
            pass

        # API 2: Web detail API (Fallback)
        web_api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={aweme_id}&aid=6383&version_code=190500&version_name=19.5.0&device_platform=webapp&os=ios"
        desktop_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Referer": f"https://www.douyin.com/video/{aweme_id}",
            "Accept": "application/json, text/plain, */*",
            "Cookie": "s_v_web_id=verify_placeholder; passport_csrf_token=placeholder;",
        }

        try:
            resp = await client.get(web_api_url, headers=desktop_headers, timeout=10.0)
            if resp.status_code == 200:
                res_json = resp.json()
                detail = res_json.get("aweme_detail")
                if detail:
                    return detail
        except Exception:
            pass

        # API 2: IES Douyin iteminfo API (Fallback)
        ies_api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={aweme_id}"
        ies_headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            "Referer": "https://www.iesdouyin.com/",
        }
        try:
            resp = await client.get(ies_api_url, headers=ies_headers, timeout=10.0)
            if resp.status_code == 200:
                res_json = resp.json()
                item_list = res_json.get("item_list", [])
                if item_list and len(item_list) > 0:
                    return item_list[0]
        except Exception:
            pass

        # API 3: Web Page SSR / Share Pages Data Extraction (Fallback 2)
        share_pages = [
            f"https://www.iesdouyin.com/share/video/{aweme_id}/",
            f"https://www.iesdouyin.com/share/note/{aweme_id}/",
            f"https://www.iesdouyin.com/share/slides/{aweme_id}/",
            f"https://www.douyin.com/video/{aweme_id}"
        ]
        for sp in share_pages:
            try:
                resp = await client.get(sp, timeout=8.0)
                if resp.status_code == 200:
                    html = resp.text
                    # Check window._ROUTER_DATA
                    r_match = re.search(r'window\._ROUTER_DATA\s*=\s*(\{.*?\})\s*</script>', html, re.DOTALL)
                    if r_match:
                        r_data = json.loads(r_match.group(1))
                        loader = r_data.get("loaderData", {})
                        for k, v in loader.items():
                            if isinstance(v, dict):
                                if "videoInfoRes" in v:
                                    items = v["videoInfoRes"].get("item_list", [])
                                    if items:
                                        return items[0]
                                if "itemInfo" in v:
                                    struct = v["itemInfo"].get("itemStruct")
                                    if struct:
                                        return struct
                                if "itemStruct" in v:
                                    return v["itemStruct"]
                    # Check RENDER_DATA
                    match = re.search(r'<script id="RENDER_DATA" type="application/json">(.+?)</script>', html)
                    if match:
                        raw_data = urllib.parse.unquote(match.group(1))
                        data = json.loads(raw_data)
                        for key, val in data.items():
                            if isinstance(val, dict) and "aweme" in val:
                                detail = val.get("aweme", {}).get("detail")
                                if detail:
                                    return detail
            except Exception:
                pass

        return None

    def _format_result(self, detail: Dict[str, Any], raw_url: str) -> ParseResult:
        try:
            with open('G:/Antigravity_Data/scratch/raw_aweme_detail.json', 'w', encoding='utf-8') as f:
                json.dump(detail, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        aweme_id = str(detail.get("aweme_id", ""))
        desc = detail.get("desc", "").strip() or "无标题作品"
        
        # Author information
        author_data = detail.get("author", {})
        avatar_urls = author_data.get("avatar_thumb", {}).get("url_list", []) or author_data.get("avatar_medium", {}).get("url_list", [])
        author = AuthorInfo(
            nickname=author_data.get("nickname", "抖音用户"),
            uid=author_data.get("unique_id") or author_data.get("short_id") or str(author_data.get("uid", "")),
            avatar=avatar_urls[0] if avatar_urls else None,
            signature=author_data.get("signature", "")
        )

        # Statistics
        stats_data = detail.get("statistics", {})
        stats = Statistics(
            likes=stats_data.get("digg_count", 0),
            comments=stats_data.get("comment_count", 0),
            shares=stats_data.get("share_count", 0),
            collects=stats_data.get("collect_count", 0)
        )

        # Music
        music_data = detail.get("music", {})
        music_url = None
        if music_data:
            m_urls = music_data.get("play_url", {}).get("url_list", [])
            if m_urls:
                music_url = m_urls[0]
        music_title = music_data.get("title", "")
        music_author = music_data.get("author", "")

        # Check media type: Image Album, Live Photo, or Video
        images_data = detail.get("images", [])
        has_images = bool(images_data and len(images_data) > 0)
        
        # Check Live Photos (实况图)
        live_photos: List[LivePhotoItem] = []
        has_live_photo = False
        image_urls: List[str] = []

        if has_images:
            for idx, img in enumerate(images_data):
                # Highest quality image URL
                img_url_list = img.get("url_list", []) or img.get("download_url_list", [])
                img_url = img_url_list[-1] if img_url_list else ""
                if not img_url and img_url_list:
                    img_url = img_url_list[0]
                
                # Check for live photo dynamic video clip
                clip_video_list = img.get("clip_video_list", []) or img.get("video_list", []) or []
                clip_url = None
                if clip_video_list:
                    # Extract highest bitrate clip URL
                    for clip in clip_video_list:
                        if isinstance(clip, dict):
                            urls = clip.get("main_url") or clip.get("play_addr", {}).get("url_list", []) or clip.get("url_list", [])
                            if urls:
                                clip_url = urls[0] if isinstance(urls, list) else urls
                                break
                        elif isinstance(clip, str):
                            clip_url = clip
                            break

                # Also check live_photo dictionary if present
                if not clip_url and img.get("live_photo"):
                    lp = img.get("live_photo")
                    if isinstance(lp, dict):
                        lp_urls = lp.get("video_url_list", []) or lp.get("url_list", [])
                        if lp_urls:
                            clip_url = lp_urls[0]

                if clip_url:
                    has_live_photo = True

                if img_url:
                    image_urls.append(img_url)
                    live_photos.append(LivePhotoItem(
                        index=idx + 1,
                        image_url=img_url,
                        video_url=clip_url,
                        width=img.get("width"),
                        height=img.get("height")
                    ))

        # Video streams parsing
        video_data = detail.get("video", {})
        video_qualities: List[MediaQuality] = []
        main_video_url = None
        duration = video_data.get("duration", 0) / 1000.0 if video_data.get("duration") else None
        
        # 1. Parse video.bit_rate (Multi-quality / 4K / 1080P 60fps)
        bitrate_list = video_data.get("bit_rate", [])
        if bitrate_list:
            for b in bitrate_list:
                play_urls = b.get("play_addr", {}).get("url_list", [])
                if not play_urls:
                    continue
                # Clean watermark string in URL if present
                clean_url = play_urls[0].replace("playwm", "play")
                gear_name = b.get("gear_name", "")
                bit_rate_val = b.get("bit_rate", 0)
                w = b.get("width", 0) or b.get("play_addr", {}).get("width", 0)
                h = b.get("height", 0) or b.get("play_addr", {}).get("height", 0)
                fps = b.get("fps", 0)
                
                # Determine friendly label
                label = self._format_quality_label(gear_name, w, h, bit_rate_val, fps)
                
                video_qualities.append(MediaQuality(
                    label=label,
                    url=clean_url,
                    width=w,
                    height=h,
                    bitrate=bit_rate_val,
                    fps=fps,
                    size_bytes=b.get("play_addr", {}).get("data_size")
                ))

        # 2. Fallback to play_addr if bit_rate list is empty
        if not video_qualities and video_data:
            play_urls = video_data.get("play_addr", {}).get("url_list", [])
            if play_urls:
                clean_url = play_urls[0].replace("playwm", "play")
                w = video_data.get("width", 0)
                h = video_data.get("height", 0)
                label = "超高清 原画" if (w >= 1080 or h >= 1080) else "高清 720P"
                video_qualities.append(MediaQuality(
                    label=label,
                    url=clean_url,
                    width=w,
                    height=h
                ))

        # Sort qualities descending (highest resolution/bitrate first)
        video_qualities.sort(key=lambda x: (x.width or 0) * (x.height or 0) + (x.bitrate or 0), reverse=True)
        if video_qualities:
            main_video_url = video_qualities[0].url

        # Determine overall media type
        if has_live_photo:
            media_type = "live_photo"
        elif has_images:
            media_type = "images"
        else:
            media_type = "video"

        # Cover image
        cover_url = None
        if video_data.get("cover", {}).get("url_list"):
            cover_url = video_data["cover"]["url_list"][0]
        elif image_urls:
            cover_url = image_urls[0]

        return ParseResult(
            success=True,
            platform=self.platform_id,
            platform_name=self.platform_name,
            media_type=media_type,
            item_id=aweme_id,
            title=desc,
            cover_url=cover_url,
            author=author,
            stats=stats,
            video_url=main_video_url,
            video_qualities=video_qualities,
            duration=duration,
            images=image_urls,
            live_photos=live_photos,
            music_url=music_url,
            music_title=music_title,
            music_author=music_author,
            original_url=raw_url
        )

    def _format_quality_label(self, gear_name: str, w: int, h: int, bitrate: int, fps: int) -> str:
        max_dim = max(w, h)
        min_dim = min(w, h)
        
        # Check for 4K / 2K
        if max_dim >= 3840 or min_dim >= 2160 or "4k" in gear_name.lower():
            return "4K 超清原画"
        elif max_dim >= 2560 or min_dim >= 1440 or "2k" in gear_name.lower():
            return "2K 极清"
        elif max_dim >= 1920 or min_dim >= 1080 or "1080" in gear_name.lower():
            if fps >= 50 or "60" in gear_name:
                return "1080P 60帧 原画"
            elif "hdr" in gear_name.lower():
                return "1080P HDR 超清"
            return "1080P 超清"
        elif max_dim >= 1280 or min_dim >= 720 or "720" in gear_name.lower():
            return "720P 高清"
        elif "normal_540" in gear_name or "540" in gear_name:
            return "540P 标清"
        return "标准画质"
