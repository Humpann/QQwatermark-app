import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

class VercelPathFixMiddleware:
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            matched_path = headers.get(b"x-matched-path", b"").decode("latin1") or headers.get(b"x-vercel-matched-path", b"").decode("latin1")
            if matched_path:
                scope["path"] = matched_path
            elif scope.get("path", "").startswith("/api/index"):
                # Strip /api/index prefix
                sub = scope.get("path", "")[len("/api/index"):]
                scope["path"] = sub if sub else "/"
        await self.asgi_app(scope, receive, send)

handler = VercelPathFixMiddleware(app)
app = handler
