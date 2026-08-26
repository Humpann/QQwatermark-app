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
    CollectionVideoItem, MixInfo, AuthorInfo, Statistics, get_random_ua
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

                # 2. Try direct extraction from redirect response HTML
                data = self._extract_aweme_data_from_html(resp.text, aweme_id)

                # 3. If not found in initial HTML, fetch from Douyin APIs & Share pages
                if not data:
                    data = await self._fetch_douyin_data(client, aweme_id)

                if data:
                    # 阶段1：源头嗅探注入，同时支持 HTML 正则、URL 参数及 _ROUTER_DATA 递归
                    if not data.get("mix_info"):
                        injected_mix = self._extract_mix_info_from_html(resp.text)
                        if not injected_mix:
                            u_match = re.search(r'/collection/(\d+)|mix_id=(\d+)', final_url + ' ' + raw_url)
                            if u_match:
                                m_id = u_match.group(1) or u_match.group(2)
                                injected_mix = {"mix_id": m_id, "mix_name": "抖音视频合集"}
                        if injected_mix:
                            data["mix_info"] = injected_mix

                if not data:
                    return ParseResult(
                        success=False,
                        error_message="获取抖音作品详情失败，可能该内容已被删除或受权限保护",
                        platform=self.platform_id,
                        platform_name=self.platform_name,
                        original_url=raw_url
                    )

                return await self._format_result(data, raw_url)
            
            except httpx.UnsupportedProtocol as e:
                # Douyin might redirect some shortlinks directly to sslocal:// or snssdk:// to open the app
                return ParseResult(
                    success=False,
                    error_message="该抖音链接已失效或要求直接打开APP（重定向至本地协议），请尝试复制完整作品链接",
                    platform=self.platform_id,
                    platform_name=self.platform_name,
                    original_url=raw_url
                )
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
        match = re.search(r'awemeId[\'"]?\s*:\s*[\'"]?(\d+)', html)
        if match:
            return match.group(1)
        match2 = re.search(r'"aweme_id"\s*:\s*"(\d+)"', html)
        if match2:
            return match2.group(1)
        return None

    def _extract_mix_info_from_html(self, html: str) -> Optional[Dict[str, str]]:
        mix_patterns = [
            r'["\']mix_id["\']\s*:\s*["\']?(\d+)["\']?',
            r'mix_id[=\s]*["\']?(\d+)["\']?',
            r'/collection/(\d+)',
            r'collection_id[=\s]*["\']?(\d+)',
            r'["\']mixId["\']\s*:\s*["\']?(\d+)["\']?'
        ]
        mix_id = None
        for pattern in mix_patterns:
            match = re.search(pattern, html)
            if match:
                mix_id = match.group(1)
                break
        if mix_id:
            name_match = re.search(r'["\']mix_name["\']\s*:\s*["\']([^"\']+)["\']', html) or re.search(r'["\']mixName["\']\s*:\s*["\']([^"\']+)["\']', html)
            mix_name = name_match.group(1) if name_match else "抖音视频合集"
            return {"mix_id": mix_id, "mix_name": mix_name}
        return None

    def _extract_aweme_data_from_html(self, html: str, aweme_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        # 1. Try window._ROUTER_DATA
        r_match = re.search(r'window\._ROUTER_DATA\s*=\s*(\{.*?\})\s*</script>', html, re.DOTALL)
        if r_match:
            try:
                r_data = json.loads(r_match.group(1))
                res = self._find_aweme_recursive(r_data, aweme_id)
                if res:
                    return res
            except Exception:
                pass

        # 2. Try RENDER_DATA
        match = re.search(r'<script id="RENDER_DATA" type="application/json">(.+?)</script>', html)
        if match:
            try:
                raw_data = urllib.parse.unquote(match.group(1))
                data = json.loads(raw_data)
                res = self._find_aweme_recursive(data, aweme_id)
                if res:
                    return res
            except Exception:
                pass

        # 3. Try any JSON block inside script tags containing "aweme_detail" or "itemStruct" or "images"
        for s_match in re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
            script_text = s_match.group(1).strip()
            if "images" in script_text or "aweme_detail" in script_text or "videoInfoRes" in script_text:
                json_matches = re.finditer(r'(\{[\s\S]*\})', script_text)
                for jm in json_matches:
                    try:
                        cand = json.loads(jm.group(1))
                        res = self._find_aweme_recursive(cand, aweme_id)
                        if res:
                            return res
                    except Exception:
                        pass
        return None

    def _find_aweme_recursive(self, obj: Any, aweme_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if isinstance(obj, dict):
            has_id = (not aweme_id) or (str(obj.get("aweme_id", "")) == str(aweme_id)) or (str(obj.get("id", "")) == str(aweme_id))
            if has_id and ("images" in obj or "video" in obj or "desc" in obj or "music" in obj):
                if "images" in obj or "video" in obj or "author" in obj:
                    return obj
            for k, v in obj.items():
                res = self._find_aweme_recursive(v, aweme_id)
                if res:
                    return res
        elif isinstance(obj, list):
            for item in obj:
                res = self._find_aweme_recursive(item, aweme_id)
                if res:
                    return res
        return None

    async def _fetch_douyin_data(self, client: httpx.AsyncClient, aweme_id: str) -> Optional[Dict[str, Any]]:
        # API 1: Feed Direct API (Strict aweme_id verification, never fallback to random trending videos)
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
        except Exception:
            pass

        # API 2: Web detail API (Supports both Videos and HD Image Albums / Notes)
        web_api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={aweme_id}&aid=6383&version_code=190500&version_name=19.5.0&device_platform=webapp&os=ios"
        desktop_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Referer": f"https://www.douyin.com/video/{aweme_id}",
            "Accept": "application/json, text/plain, */*",
            "Cookie": "s_v_web_id=verify_placeholder; passport_csrf_token=placeholder; ttwid=1%7Cplaceholder%7Cplaceholder;",
        }

        try:
            resp = await client.get(web_api_url, headers=desktop_headers, timeout=10.0)
            if resp.status_code == 200:
                res_json = resp.json()
                detail = res_json.get("aweme_detail")
                if detail and str(detail.get("aweme_id", "")) == str(aweme_id):
                    return detail
                elif detail and not detail.get("aweme_id"):
                    return detail
        except Exception:
            pass

        # API 3: IES Douyin iteminfo API
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
                    for it in item_list:
                        if str(it.get("aweme_id")) == str(aweme_id) or str(it.get("id")) == str(aweme_id):
                            return it
                    return item_list[0]
        except Exception:
            pass

        # API 4: Share pages SSR extraction
        share_pages = [
            f"https://www.iesdouyin.com/share/note/{aweme_id}/",
            f"https://www.iesdouyin.com/share/slides/{aweme_id}/",
            f"https://www.iesdouyin.com/share/video/{aweme_id}/",
            f"https://www.douyin.com/note/{aweme_id}",
            f"https://www.douyin.com/video/{aweme_id}"
        ]
        for sp in share_pages:
            try:
                resp = await client.get(sp, timeout=8.0)
                if resp.status_code == 200:
                    extracted = self._extract_aweme_data_from_html(resp.text, aweme_id)
                    if extracted:
                        return extracted
            except Exception:
                pass

        return None

    async def _format_result(self, detail: Dict[str, Any], raw_url: str) -> ParseResult:
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
        images_data = (
            detail.get("images") or
            detail.get("image_post_info", {}).get("images") or
            detail.get("image_post_info", {}).get("image_list") or
            detail.get("image_post_info", {}).get("post_images") or
            detail.get("images_info", {}).get("images") or
            detail.get("img_list") or
            detail.get("image_infos") or
            detail.get("image_list") or
            detail.get("slides") or
            detail.get("post_images") or
            []
        )
        has_images = bool(images_data and len(images_data) > 0)
        
        # Check Live Photos (实况图)
        live_photos: List[LivePhotoItem] = []
        has_live_photo = False
        image_urls: List[str] = []

        if has_images:
            for idx, img in enumerate(images_data):
                if isinstance(img, str):
                    image_urls.append(img)
                    continue
                # Strictly pick clean, unwatermarked 4K/1080P original image URL
                candidates = []
                for k in ["url_list", "origin_image", "display_image", "thumbnail", "download_url_list"]:
                    val = img.get(k)
                    if isinstance(val, dict):
                        val = val.get("url_list")
                    if isinstance(val, list):
                        candidates.extend(val)

                clean_candidates = [u for u in candidates if isinstance(u, str) and "-water:" not in u and "_water" not in u and "watermark" not in u]
                target_list = clean_candidates if clean_candidates else candidates

                clean_jpegs = [u for u in target_list if ".jpeg" in u or ".jpg" in u or ".png" in u]
                if clean_jpegs:
                    img_url = clean_jpegs[-1]
                elif target_list:
                    img_url = target_list[-1]
                else:
                    img_url = img.get("url") or img.get("image_url") or ""

                if not img_url and img.get("uri"):
                    img_url = f"https://p3-pc.douyinpic.com/{img.get('uri')}~tplv-dy-aweme-images:1080p.jpeg"
                
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

        # Check Mix / Video Collection (合集 / 视频集 / 连续剧集)
        mix_data = detail.get("mix_info") or detail.get("mix_item") or detail.get("mix")
        collection_videos: List[CollectionVideoItem] = []
        mix_info_obj: Optional[MixInfo] = None

        if mix_data and isinstance(mix_data, dict):
            mix_id = str(mix_data.get("mix_id") or mix_data.get("id") or "")
            mix_name = mix_data.get("mix_name") or mix_data.get("name") or "抖音视频合集"
            total_count = mix_data.get("st_count") or mix_data.get("all_count") or mix_data.get("sub_items_count") or 0
            curr_ep = mix_data.get("current_episode") or 1
            
            if mix_id:
                mix_info_obj = MixInfo(
                    mix_id=mix_id,
                    mix_name=mix_name,
                    total_count=int(total_count) if total_count else 0,
                    current_episode=int(curr_ep) if curr_ep else 1
                )
                try:
                    collection_videos = await self._fetch_douyin_mix_videos(mix_id)
                except Exception:
                    pass

        aweme_type = detail.get("aweme_type", 0)
        is_explicit_image = (aweme_type in (68, 2, 150)) and (not main_video_url or not video_qualities or len(image_urls) > 0)

        if is_explicit_image and not image_urls and not main_video_url:
            cover_candidate = (
                video_data.get("cover", {}).get("url_list", [None])[0] or
                video_data.get("origin_cover", {}).get("url_list", [None])[0] or
                video_data.get("dynamic_cover", {}).get("url_list", [None])[0]
            )
            if cover_candidate:
                image_urls.append(cover_candidate)
                has_images = True

        # Determine overall media type
        if collection_videos and len(collection_videos) > 1:
            media_type = "collection"
            image_urls = []
            live_photos = []
        elif has_live_photo:
            media_type = "live_photo"
        elif image_urls and len(image_urls) > 0:
            media_type = "images"
        else:
            media_type = "video"

        # Cover image
        cover_url = None
        if video_data.get("cover", {}).get("url_list"):
            cover_url = video_data["cover"]["url_list"][0]
        elif image_urls:
            cover_url = image_urls[0]
        elif collection_videos and collection_videos[0].cover_url:
            cover_url = collection_videos[0].cover_url

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
            mix_info=mix_info_obj,
            collection_videos=collection_videos,
            music_url=music_url,
            music_title=music_title,
            music_author=music_author,
            original_url=raw_url
        )

    async def _fetch_douyin_mix_videos(self, mix_id: str) -> List[CollectionVideoItem]:
        items: List[CollectionVideoItem] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Referer": f"https://www.douyin.com/collection/{mix_id}",
            "Accept": "application/json, text/plain, */*"
        }
        
        urls = [
            f"https://www.douyin.com/aweme/v1/web/mix/aweme/?mix_id={mix_id}&cursor=0&count=50&aid=6383&device_platform=webapp",
            f"https://aweme.snssdk.com/aweme/v1/mix/aweme/?mix_id={mix_id}&cursor=0&count=50&aid=1128"
        ]
        
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=10.0) as client:
            for u in urls:
                try:
                    resp = await client.get(u)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        aweme_list = res_json.get("aweme_list", []) or res_json.get("mix_items", [])
                        if aweme_list:
                            for idx, aw in enumerate(aweme_list):
                                v_data = aw.get("video", {})
                                play_urls = []
                                bitrates = v_data.get("bit_rate", [])
                                if bitrates:
                                    for b in bitrates:
                                        p_list = b.get("play_addr", {}).get("url_list", [])
                                        if p_list:
                                            play_urls.append(p_list[0].replace("playwm", "play"))
                                if not play_urls and v_data.get("play_addr", {}).get("url_list"):
                                    play_urls.append(v_data["play_addr"]["url_list"][0].replace("playwm", "play"))
                                
                                clean_v_url = play_urls[0] if play_urls else ""
                                if clean_v_url:
                                    c_urls = v_data.get("cover", {}).get("url_list", [])
                                    cover = c_urls[0] if c_urls else None
                                    dur = v_data.get("duration", 0) / 1000.0 if v_data.get("duration") else None
                                    ep_title = aw.get("desc", f"第 {idx+1} 集").strip()
                                    items.append(CollectionVideoItem(
                                        index=idx + 1,
                                        title=ep_title,
                                        item_id=str(aw.get("aweme_id", "")),
                                        video_url=clean_v_url,
                                        cover_url=cover,
                                        duration=dur
                                    ))
                            if items:
                                break
                except Exception:
                    pass
        return items

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
