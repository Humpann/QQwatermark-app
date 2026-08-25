import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

async def app(scope, receive, send):
    if scope["type"] == "http":
        headers = dict(scope.get("headers", []))
        for header_key in [b"x-forwarded-uri", b"x-matched-path", b"x-vercel-matched-path", b"x-invoke-path", b"x-original-url"]:
            val = headers.get(header_key)
            if val:
                raw_val = val.decode("latin1").split("?")[0]
                if raw_val and raw_val not in ["/api/index.py", "/api/index"]:
                    scope["path"] = raw_val
                    break
        else:
            p = scope.get("path", "")
            if p.startswith("/api/index.py"):
                scope["path"] = p[len("/api/index.py"):] or "/"
            elif p.startswith("/api/index"):
                scope["path"] = p[len("/api/index"):] or "/"

    await fastapi_app(scope, receive, send)

handler = app
