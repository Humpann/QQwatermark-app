# -*- coding: utf-8 -*-
"""
PureClip QQ · 云端开发者总控服务一键启动器
端口: 8888 (局域网 + 本地双模开放)
"""
import os
import sys
import io
import asyncio

# Force UTF-8 standard streams on Windows
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("=========================================================================")
    print("  [PureClip QQ] Developer Cloud Admin Hub Online")
    print("  Super Admin: QQ (dev_qq_official) | VIP Target: 成雨萌")
    print("  Server Address: http://127.0.0.1:8888 (Local) | http://0.0.0.0:8888 (LAN)")
    print("=========================================================================")
    
    # 强制采用 Windows Selector 事件循环，彻底免疫 Proactor WinError 64 崩溃
    loop = asyncio.WindowsSelectorEventLoopPolicy().new_event_loop()
    asyncio.set_event_loop(loop)
    
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8888, log_level="info", loop="asyncio", access_log=False)
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
