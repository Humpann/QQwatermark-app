# 🌟 OmniMedia 4K Pro · 短视频与实况图集无水印全能提取系统 v5.0

> **QQ / 成雨萌 尊享旗舰定制版**
> 全平台 4K 原画 1:1 无损提取 · 实况 Live 动图 · 独立高音质 BGM · 实时大屏流遥测 · 智能差量相册协同

---

## 🎯 核心架构与功能亮点

1. **多端协同与全栈架构**：
   - **后端引擎**：Python 3.10+ / FastAPI / Uvicorn 高并发异步架构，内置抖音、快手多平台智能破盾解析与直链提取；
   - **前端界面**：Apple iOS / Cupertino Minimal & Liquid Glass（流体磨砂玻璃）高质感设计，支持移动端视口自适应与居中模态；
   - **Android 客户端**：原生 Kotlin + Chromium 沙箱 WebView 混合架构，支持剪贴板无感破盾、相册差量监听与大屏流遥测。

2. **4K 原画 1:1 官方顶级 CDN 源直取**：
   - 提取官方顶级无损 4K 视频流与实况原图，绝不二次压缩；
   - 完美支持实况动图（Live Photos）及独立配乐（BGM）一键分离提取。

3. **管理后台与大屏协同 (`/admin`)**：
   - 实时设备状态监控、网络延迟遥测与屏幕流传输；
   - 差量相册备份分析与管理；
   - 管理员全局翻页广播弹窗与即时互动。

---

## 📂 项目工程目录结构

```
QQwatermark-app/
├── app/                  # FastAPI 后端核心源码
│   ├── parsers/          # 各平台解析器 (Douyin, Kuaishou 等)
│   ├── services/         # AI 智能相册与分析服务
│   ├── static/           # 静态资源与样式
│   ├── admin_view.py     # 管理后台控制台大屏
│   └── main.py           # API 路由与服务端主入口
├── android/              # Android Studio 原生工程
│   ├── app/              # Android 应用源码与资源
│   │   └── src/main/assets/index.html  # Cupertino 客户端 UI
│   ├── build.gradle.kts  # Gradle 8.5 构建配置
│   └── gradlew.bat       # Gradle 包装器
├── index.html            # 单文件便携版 Web 客户端
├── requirements.txt      # Python 依赖清单
├── Dockerfile            # 容器化部署文件
└── vercel.json           # Serverless 部署配置
```

---

## 🚀 免费云端部署与二级域名绑定指南

### 方式一：Zeabur / Render 免费云端部署（24 小时在线）
1. 打开 [Render.com](https://render.com) 或 [Zeabur.com](https://zeabur.com)，使用 GitHub 账号登录；
2. 选择导入本仓库 `Humpann/QQwatermark-app`；
3. 选择 Python 环境，构建命令填入 `pip install -r requirements.txt`，启动命令填入 `uvicorn app.main:app --host 0.0.0.0 --port $PORT`；
4. 进入 **Custom Domains** 填入你的二级域名（如 `api.yourdomain.com`），添加 CNAME 解析即可全自动下发免费 HTTPS 证书！

### 方式二：Cloudflare Tunnel 本地内网穿透（0 费用 · 极速）
```powershell
# 1. 创建并启动隧道
cloudflared tunnel create watermark-tunnel
cloudflared tunnel route dns watermark-tunnel api.yourdomain.com
cloudflared tunnel run --url http://localhost:8888 watermark-tunnel
```

---

## 📱 Android 客户端编译与真机运行

1. 打开 **Android Studio**，选择 `Open` 并打开本仓库下的 `android` 文件夹；
2. 配置 Gradle JDK 为 **JDK 21**（或 JDK 17）；
3. 点击右上角 **🐘 Sync Project with Gradle Files**；
4. 连接手机开启 USB 调试，点击 **▶️ Run 'app'** 即可一键安装体验！

---

## ⚖️ 免责声明

本工具仅供技术交流与个人媒体原件备份使用，所有提取的音视频与图集版权归原作者及所属平台所有。严禁用于任何商业侵权或非法用途。
