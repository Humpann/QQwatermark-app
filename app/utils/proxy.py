"""
Streaming proxy and ZIP packager to bypass CDN anti-hotlinking and support downloads.
"""
import io
import zipfile
import urllib.parse
from typing import AsyncGenerator, Dict, List, Optional
import httpx
from fastapi import Response
from starlette.responses import StreamingResponse

DEFAULT_PROXY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Accept": "*/*",
}

def get_platform_headers(url: str, custom_range: Optional[str] = None) -> Dict[str, str]:
    headers = DEFAULT_PROXY_HEADERS.copy()
    if "douyin" in url or "iesdouyin" in url:
        headers["Referer"] = "https://www.douyin.com/"
    elif "kuaishou" in url or "kwai" in url or "yximgs" in url:
        headers["Referer"] = "https://www.kuaishou.com/"
    
    if custom_range:
        headers["Range"] = custom_range
    return headers

async def stream_remote_media(
    url: str,
    range_header: Optional[str] = None,
    filename: Optional[str] = None,
    as_attachment: bool = False
) -> StreamingResponse:
    """Stream media chunks from target URL, forwarding Range headers for seeking."""
    headers = get_platform_headers(url, range_header)
    
    client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    req = client.build_request("GET", url, headers=headers)
    resp = await client.send(req, stream=True)

    status_code = resp.status_code
    response_headers = {}
    
    # Copy essential headers
    for h in ["content-type", "content-length", "content-range", "accept-ranges"]:
        if h in resp.headers:
            response_headers[h] = resp.headers[h]

    if "accept-ranges" not in response_headers:
        response_headers["accept-ranges"] = "bytes"

    if as_attachment and filename:
        encoded_filename = urllib.parse.quote(filename)
        response_headers["content-disposition"] = f"attachment; filename=\"{encoded_filename}\"; filename*=UTF-8''{encoded_filename}"

    async def content_iterator() -> AsyncGenerator[bytes, None]:
        try:
            async for chunk in resp.aiter_bytes(chunk_size=64 * 1024):
                yield chunk
        finally:
            await resp.aclose()
            await client.aclose()

    return StreamingResponse(
        content_iterator(),
        status_code=status_code,
        headers=response_headers,
        media_type=resp.headers.get("content-type", "application/octet-stream")
    )

async def create_zip_archive(urls_with_names: List[Dict[str, str]]) -> io.BytesIO:
    """Download multiple media files asynchronously and pack into an in-memory ZIP."""
    zip_buffer = io.BytesIO()
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for item in urls_with_names:
                url = item.get("url")
                name = item.get("name", "media_file")
                if not url:
                    continue
                try:
                    headers = get_platform_headers(url)
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        zip_file.writestr(name, resp.content)
                except Exception as e:
                    print(f"Error downloading {name} for ZIP: {e}")
                    
    zip_buffer.seek(0)
    return zip_buffer
