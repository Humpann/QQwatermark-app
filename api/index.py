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

from fastapi.responses import JSONResponse
from fastapi import Request

@fastapi_app.middleware("http")
async def debug_headers_middleware(request: Request, call_next):
    if "debug" in request.url.path or request.headers.get("x-debug") == "1":
        return JSONResponse({
            "url": str(request.url),
            "path": request.url.path,
            "headers": dict(request.headers),
            "scope_path": request.scope.get("path"),
            "scope_raw_path": str(request.scope.get("raw_path")),
            "scope_root_path": request.scope.get("root_path")
        })
    return await call_next(request)

class VercelPathFixMiddleware:
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            raw_path = scope.get("path", "")
            
            # Extract actual URL path from Vercel headers
            forwarded = headers.get(b"x-forwarded-uri", b"").decode("latin1")
            matched = headers.get(b"x-matched-path", b"").decode("latin1")
            invoke = headers.get(b"x-invoke-path", b"").decode("latin1")
            
            target = None
            if forwarded:
                target = forwarded.split("?")[0]
            elif invoke:
                target = invoke.split("?")[0]
            elif matched and not matched.startswith("/api/index"):
                target = matched.split("?")[0]
            elif raw_path.startswith("/api/index"):
                sub = raw_path[len("/api/index"):]
                target = sub if sub else "/"
                
            if target:
                scope["path"] = target
                
        await self.asgi_app(scope, receive, send)

handler = VercelPathFixMiddleware(fastapi_app)
app = handler
