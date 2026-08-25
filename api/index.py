import os
import sys
import traceback

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.main import app as fastapi_app
except Exception as e:
    err_msg = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse
    fastapi_app = FastAPI()
    @fastapi_app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        return PlainTextResponse(f"FastAPI Import Error on Vercel:\n\n{err_msg}", status_code=500)

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

handler = VercelPathFixMiddleware(fastapi_app)
app = handler
