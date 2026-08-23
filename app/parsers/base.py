"""
Base parser definitions, data models, and common utilities.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import re
import random
import httpx

USER_AGENTS = [
    # Desktop Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    # Mobile Chrome / Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
]

def get_random_ua(mobile: bool = False) -> str:
    if mobile:
        return USER_AGENTS[2]
    return USER_AGENTS[0]

class MediaQuality(BaseModel):
    label: str = Field(description="4K, 2K, 1080P, 720P, etc.")
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    bitrate: Optional[int] = None
    fps: Optional[int] = None
    size_bytes: Optional[int] = None

class LivePhotoItem(BaseModel):
    index: int
    image_url: str
    video_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

class AuthorInfo(BaseModel):
    nickname: str = "未知作者"
    uid: Optional[str] = None
    avatar: Optional[str] = None
    signature: Optional[str] = None

class Statistics(BaseModel):
    likes: int = 0
    comments: int = 0
    shares: int = 0
    collects: int = 0

class ParseResult(BaseModel):
    success: bool = True
    error_message: Optional[str] = None
    platform: str = "unknown"  # douyin, kuaishou, etc.
    platform_name: str = "未知平台"
    media_type: str = "video"  # "video", "images", "live_photo"
    item_id: str = ""
    title: str = ""
    cover_url: Optional[str] = None
    author: AuthorInfo = Field(default_factory=AuthorInfo)
    stats: Statistics = Field(default_factory=Statistics)
    
    # Video fields
    video_url: Optional[str] = None  # Highest quality video stream
    video_qualities: List[MediaQuality] = Field(default_factory=list)
    duration: Optional[float] = None
    
    # Image Album fields
    images: List[str] = Field(default_factory=list)
    
    # Live Photo fields
    live_photos: List[LivePhotoItem] = Field(default_factory=list)
    
    # Audio fields
    music_url: Optional[str] = None
    music_title: Optional[str] = None
    music_author: Optional[str] = None
    
    # Metadata
    original_url: str = ""

class BaseParser:
    """Abstract Base Class for Video/Image Parsers"""
    platform_id: str = "base"
    platform_name: str = "Base"

    def match(self, url: str) -> bool:
        raise NotImplementedError

    async def parse(self, text_or_url: str) -> ParseResult:
        raise NotImplementedError

    @staticmethod
    def extract_url(text: str) -> Optional[str]:
        """Extract HTTP/HTTPS URL from raw user text or share snippets."""
        pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[^\s\u4e00-\u9fa5]*)?'
        match = re.search(pattern, text)
        if match:
            return match.group(0).rstrip('。，；！？)）')
        return None
