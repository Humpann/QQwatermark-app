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

app = fastapi_app
handler = fastapi_app
