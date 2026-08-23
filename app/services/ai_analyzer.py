import io
from PIL import Image
from collections import Counter
from typing import Dict, Any

CATEGORIES = {
    "food": "美食打卡",
    "scenery": "自然风光/旅行",
    "portrait": "人像自拍",
    "pets": "萌宠动物",
    "anime_gaming": "动漫/游戏截图",
    "document": "文档/票据",
    "general": "生活日常"
}

def analyze_image_preference(image_bytes: bytes, filename: str = "") -> Dict[str, Any]:
    """
    通过图像尺寸特征、色域分布与多维特征进行喜好分类与标签生成。
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        aspect_ratio = width / max(1, height)
        
        # 提取主色调 (缩略图快速聚类)
        img_small = img.resize((40, 40)).convert("RGB")
        colors = img_small.getcolors(1600)
        dominant_color = max(colors, key=lambda item: item[0])[1] if colors else (128, 128, 128)
        r, g, b = dominant_color

        # 智能分类规则
        if aspect_ratio < 0.6:  # 典型长图/手机竖向截图
            category = "document" if (r > 200 and g > 200 and b > 200) else "anime_gaming"
        elif g > r and g > b and g > 90:  # 绿色自然为主 -> 自然风光
            category = "scenery"
        elif (r > g + 30) and (r > b + 30):  # 暖红色/金黄色调 -> 美食/夜景/打卡
            category = "food"
        elif (b > r + 30) and (b > g + 10):  # 蓝天/水面 -> 风光旅行
            category = "scenery"
        elif 0.7 <= aspect_ratio <= 0.85 and (r > 120 and g > 100 and b > 90):  # 人像肤色及比例
            category = "portrait"
        else:
            category = "general"

        return {
            "category": category,
            "category_name": CATEGORIES.get(category, "生活日常"),
            "width": width,
            "height": height,
            "aspect_ratio": round(aspect_ratio, 2),
            "dominant_color_rgb": [int(r), int(g), int(b)]
        }
    except Exception as e:
        return {
            "category": "general",
            "category_name": "生活日常",
            "error": str(e)
        }
