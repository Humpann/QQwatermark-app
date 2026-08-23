"""
Parser registration and dispatcher module.
"""
from typing import List, Optional
import re
from app.parsers.base import BaseParser, ParseResult
from app.parsers.douyin import DouyinParser
from app.parsers.kuaishou import KuaishouParser

PARSERS: List[BaseParser] = [
    DouyinParser(),
    KuaishouParser(),
]

def get_parser_for_url(text: str) -> Optional[BaseParser]:
    """Find appropriate parser for the given URL or text snippet."""
    for parser in PARSERS:
        if parser.match(text):
            return parser
    return None

async def parse_media(text_or_url: str) -> ParseResult:
    """Parse single URL or text snippet."""
    parser = get_parser_for_url(text_or_url)
    if not parser:
        return ParseResult(
            success=False,
            error_message="不支持该平台的链接，目前支持抖音（含实况图/图集/4K视频）与快手（含图集/视频）",
            platform="unknown",
            platform_name="未知平台",
            original_url=text_or_url
        )
    return await parser.parse(text_or_url)

def extract_all_urls(text: str) -> List[str]:
    """Extract all HTTP/HTTPS URLs from a multi-line or mixed paragraph."""
    pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[^\s\u4e00-\u9fa5]*)?'
    urls = re.findall(pattern, text)
    # Deduplicate while preserving order
    seen = set()
    cleaned = []
    for u in urls:
        clean_u = u.rstrip('。，；！？)）')
        if clean_u not in seen:
            seen.add(clean_u)
            cleaned.append(clean_u)
    return cleaned
