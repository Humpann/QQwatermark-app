import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

async def app(scope, receive, send):
    if scope["type"] == "http":
        p = scope.get("path", "")
        if not p.startswith("/"):
            p = "/" + p
        if p.startswith("/api/index.py"):
            p = p[len("/api/index.py"):] or "/"
        elif p.startswith("/api/index"):
            p = p[len("/api/index"):] or "/"
        scope["path"] = p

    await fastapi_app(scope, receive, send)

handler = app
