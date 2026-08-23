"""
Kuaishou (快手) parser supporting 4K/HD Videos, Image Albums, and Music.
"""
import re
import json
import urllib.parse
from typing import Optional, List, Dict, Any
import httpx

from app.parsers.base import (
    BaseParser, ParseResult, MediaQuality, LivePhotoItem,
    AuthorInfo, Statistics
)

class KuaishouParser(BaseParser):
    platform_id = "kuaishou"
    platform_name = "快手"

    KUAISHOU_URL_PATTERN = re.compile(
        r'https?://(?:www\.|v\.|live\.|c\.|video\.|gifshow\.)?(?:kuaishou|kwai|gifshow)\.com/[^\s\u4e00-\u9fa5]+'
    )

    def match(self, text: str) -> bool:
        return bool(self.KUAISHOU_URL_PATTERN.search(text)) or "kuaishou.com" in text or "kwai.com" in text

    async def parse(self, text_or_url: str) -> ParseResult:
        raw_url = self.extract_url(text_or_url)
        if not raw_url:
            return ParseResult(
                success=False,
                error_message="未在输入中检测到有效的快手链接",
                platform=self.platform_id,
                platform_name=self.platform_name,
                original_url=text_or_url
            )

        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": "did=web_placeholder; client_key=65890b29; country_code=CN;",
        }

        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15.0) as client:
            try:
                resp = await client.get(raw_url)
                final_url = str(resp.url)
                html_content = resp.text

                # 1. Try extracting state from HTML
                data = self._extract_state_from_html(html_content)
                
                # 2. If not found, try GraphQL or H5 query using photo_id
                if not data:
                    photo_id = self._extract_photo_id(final_url) or self._extract_photo_id(html_content)
                    if photo_id:
                        data = await self._fetch_kuaishou_graphql(client, photo_id)

                if not data:
                    return ParseResult(
                        success=False,
                        error_message="无法解析该快手内容，可能已被删除、设为私密或链接失效",
                        platform=self.platform_id,
                        platform_name=self.platform_name,
                        original_url=raw_url
                    )

                return self._format_result(data, raw_url)

            except Exception as e:
                return ParseResult(
                    success=False,
                    error_message=f"解析快手内容时发生错误: {str(e)}",
                    platform=self.platform_id,
                    platform_name=self.platform_name,
                    original_url=raw_url
                )

    def _extract_photo_id(self, text: str) -> Optional[str]:
        patterns = [
            r'/short-video/([a-zA-Z0-9]+)',
            r'/photo/([a-zA-Z0-9]+)',
            r'photoId=([a-zA-Z0-9]+)',
            r'shareObjectId=([a-zA-Z0-9]+)',
            r'/u/[^/]+/([a-zA-Z0-9]+)',
            r'fid=([a-zA-Z0-9]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _extract_state_from_html(self, html: str) -> Optional[Dict[str, Any]]:
        # Match window.INIT_STATE or window.PAGE_DATA or window.__APOLLO_STATE__
        patterns = [
            r'window\.INIT_STATE\s*=\s*({.+?});?</script>',
            r'window\.PAGE_DATA\s*=\s*({.+?});?</script>',
            r'window\.__APOLLO_STATE__\s*=\s*({.+?});?</script>',
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});?</script>',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    # Check for photo or video info inside INIT_STATE
                    if isinstance(data, dict):
                        # Explore possible trees
                        if "photo" in data:
                            return data["photo"]
                        if "photoDetail" in data:
                            return data["photoDetail"]
                        # Nested in video / root
                        for k, v in data.items():
                            if isinstance(v, dict) and "photo" in v:
                                return v["photo"]
                            if isinstance(v, dict) and "photoDetail" in v:
                                return v["photoDetail"]
                    return data
                except Exception:
                    continue

        # Regex fallback for embedded video url inside html
        match_video = re.search(r'\"photoUrl\"\s*:\s*\"(https?:[^\"]+)\"', html)
        match_caption = re.search(r'\"caption\"\s*:\s*\"([^\"]*)\"', html)
        match_user = re.search(r'\"userName\"\s*:\s*\"([^\"]*)\"', html)
        match_avatar = re.search(r'\"headUrl\"\s*:\s*\"(https?:[^\"]+)\"', html)

        if match_video:
            return {
                "photoUrl": match_video.group(1).encode().decode('unicode-escape'),
                "caption": match_caption.group(1).encode().decode('unicode-escape') if match_caption else "",
                "userName": match_user.group(1).encode().decode('unicode-escape') if match_user else "快手用户",
                "headUrl": match_avatar.group(1).encode().decode('unicode-escape') if match_avatar else "",
            }

        return None

    async def _fetch_kuaishou_graphql(self, client: httpx.AsyncClient, photo_id: str) -> Optional[Dict[str, Any]]:
        url = "https://www.kuaishou.com/graphql"
        query = """
        query videoDetail($photoId: String) {
          visionVideoDetail(photoId: $photoId) {
            status
            photo {
              id
              duration
              caption
              likeCount
              viewCount
              commentCount
              coverUrl
              photoUrl
              mainMvUrls {
                quality
                url
              }
              userName
              userSex
              headUrl
              userId
              ext_params {
                atlas {
                  list
                  cdn
                }
              }
            }
          }
        }
        """
        payload = {
            "operationName": "videoDetail",
            "variables": {"photoId": photo_id},
            "query": query
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Referer": "https://www.kuaishou.com/",
            "Content-Type": "application/json"
        }
        try:
            resp = await client.post(url, json=payload, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                res_json = resp.json()
                detail = res_json.get("data", {}).get("visionVideoDetail", {}).get("photo")
                if detail:
                    return detail
        except Exception:
            pass
        return None

    def _format_result(self, photo: Dict[str, Any], raw_url: str) -> ParseResult:
        # Check nested photo structure
        if "photo" in photo and isinstance(photo["photo"], dict):
            photo = photo["photo"]

        photo_id = str(photo.get("id") or photo.get("photoId") or "")
        caption = photo.get("caption") or photo.get("title") or photo.get("desc") or "快手作品"

        # Author info
        user_name = photo.get("userName") or photo.get("authorName") or photo.get("author", {}).get("name") or "快手用户"
        user_id = str(photo.get("userId") or photo.get("author", {}).get("id") or "")
        head_url = photo.get("headUrl") or photo.get("author", {}).get("avatar") or photo.get("author", {}).get("headerUrl")
        
        author = AuthorInfo(
            nickname=user_name,
            uid=user_id,
            avatar=head_url,
            signature=photo.get("userSignature", "")
        )

        # Stats
        stats = Statistics(
            likes=photo.get("likeCount", 0) or photo.get("realLikeCount", 0),
            comments=photo.get("commentCount", 0),
            shares=photo.get("shareCount", 0),
            collects=photo.get("viewCount", 0)
        )

        # Video Qualities
        video_qualities: List[MediaQuality] = []
        main_video_url = None

        # 1. mainMvUrls (multi-definition)
        main_mv_urls = photo.get("mainMvUrls", [])
        if main_mv_urls:
            for mv in main_mv_urls:
                if isinstance(mv, dict):
                    v_url = mv.get("url")
                    quality_str = mv.get("quality", "原画")
                    if v_url:
                        video_qualities.append(MediaQuality(
                            label=self._format_kuaishou_quality(quality_str),
                            url=v_url
                        ))

        # 2. single photoUrl
        single_photo_url = photo.get("photoUrl") or photo.get("videoUrl") or photo.get("playUrl")
        if single_photo_url:
            if not any(q.url == single_photo_url for q in video_qualities):
                video_qualities.append(MediaQuality(
                    label="超清 原画",
                    url=single_photo_url
                ))

        if video_qualities:
            main_video_url = video_qualities[0].url

        # Check for Image Album (Atlas)
        image_urls: List[str] = []
        live_photos: List[LivePhotoItem] = []
        
        atlas_data = photo.get("ext_params", {}).get("atlas") or photo.get("atlas")
        if isinstance(atlas_data, dict):
            cdn_hosts = atlas_data.get("cdn", [])
            cdn_prefix = f"https://{cdn_hosts[0]}" if cdn_hosts else "https://p1.a.yximgs.com"
            path_list = atlas_data.get("list", [])
            for p in path_list:
                if p.startswith("http"):
                    image_urls.append(p)
                else:
                    image_urls.append(f"{cdn_prefix}{p}")

        # Also check direct images list
        direct_images = photo.get("images") or photo.get("imageUrls") or []
        if isinstance(direct_images, list):
            for img in direct_images:
                if isinstance(img, str) and img.startswith("http") and img not in image_urls:
                    image_urls.append(img)
                elif isinstance(img, dict) and img.get("url"):
                    image_urls.append(img["url"])

        # Populate live photos structure for consistency
        for idx, img_u in enumerate(image_urls):
            live_photos.append(LivePhotoItem(
                index=idx + 1,
                image_url=img_u,
                video_url=None
            ))

        # Music info
        music_url = photo.get("soundTrack", {}).get("audioUrl") or photo.get("music", {}).get("playUrl")
        music_title = photo.get("soundTrack", {}).get("name") or photo.get("music", {}).get("title")

        cover_url = photo.get("coverUrl") or photo.get("poster") or (image_urls[0] if image_urls else None)
        duration = (photo.get("duration", 0) / 1000.0) if photo.get("duration") else None

        media_type = "images" if (image_urls and not main_video_url) else "video"

        return ParseResult(
            success=True,
            platform=self.platform_id,
            platform_name=self.platform_name,
            media_type=media_type,
            item_id=photo_id,
            title=caption,
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
            original_url=raw_url
        )

    def _format_kuaishou_quality(self, q: str) -> str:
        q_lower = q.lower()
        if "4k" in q_lower or "uhd" in q_lower:
            return "4K 超高清"
        elif "1080" in q_lower or "fhd" in q_lower:
            return "1080P 超清"
        elif "720" in q_lower or "hd" in q_lower:
            return "720P 高清"
        elif "high" in q_lower or "origin" in q_lower:
            return "原画 超清"
        return f"{q} 画质"
