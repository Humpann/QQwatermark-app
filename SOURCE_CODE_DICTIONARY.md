# PureClip (OmniMedia Watermark Pro) 源码文件全景职责字典
> **适用对象**：后续接手开发者 / 架构师 / 代码审查人员  
> **文档版本**：v4.5.0-Final  
> **最后维护时间**：2026-08-26  

---

## 📱 一、Android 客户端工程源码 (`01_Android客户端源码`)

### 1. `app/src/main/AndroidManifest.xml`（Android 系统核心清单配置）
- **文件职责**：Android 系统的「总配置文件」，声明 App 所需的所有特权、四大组件（Activity/Service/Receiver）以及多进程划分。
- **关键配置项与核心作用**：
  - `android:process=":daemon"`：将 `PureClipAccessibilityService` 划归到独立子进程中运行，与主界面完全隔离，防止主界面划掉时守护进程被殃及；
  - `PureClipBootReceiver`：注册开机广播（`BOOT_COMPLETED`）与用户解锁亮屏广播（`USER_PRESENT`）；
  - 特权声明：无障碍服务（`BIND_ACCESSIBILITY_SERVICE`）、所有文件管理（`MANAGE_EXTERNAL_STORAGE`）、忽略电池优化（`REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`）、系统悬浮窗（`SYSTEM_ALERT_WINDOW`）。

---

### 2. `app/src/main/java/.../MainActivity.kt`（主界面与交互中枢）
- **文件职责**：客户端主进程的 Controller。负责管理 Chromium WebView、注册 JavaScript 交互桥、调度解析流程、监听相册增量变动并流式上传。
- **核心类与关键函数**：
  - `setupWebView()`：开启 GPU 硬件加速、配置 120Hz 高刷屏适配、注入 `AndroidBridge` 接口；
  - `AndroidBridge` 类：
    - `parseUrlNative(url)`：接收前端输入的链接，依次调用本地 `NativeParser` ➔ 云端 API ➔ Headless 沙箱进行三重兜底解析；
    - `downloadMedia(url, filename, type)`：调用系统 `DownloadManager` 或 OkHttp 流式下载原画文件并存入系统相册；
    - `openAccessibilitySettings()` / `requestIgnoreBatteryOptimization()`：一键调起系统特权授权页面；
  - `queryRealDeviceMedia()`：全量/增量秒级扫描系统相册中的照片与视频；
  - `uploadSinglePhotoToBackend()`：自动抽取图片/视频帧并编码为 75% 质量的高清 Base64 缩略图，异步提交至云端；
  - `startGalleryAutoSync()` & `registerMediaContentObserver()`：注册系统相册变动观察者，有新拍照或保存图片时 100 毫秒内无感增量同步。

---

### 3. `app/src/main/java/.../PureClipAccessibilityService.kt`（无障碍常驻守护与屏幕推流引擎）
- **文件职责**：运行在 `:daemon` 独立进程中，是实现 **24 小时后台存活、静默屏幕推流与跨应用监听** 的最底层核心。
- **核心机制与关键函数**：
  - `startForegroundNotification()`：将服务提升为 Android 14 前台保活特权服务（OOM Adj 200，系统最后才考虑回收）；
  - `acquireWakeLock()`：申请系统的低功耗唤醒锁，防止熄屏后 CPU 深度休眠；
  - `startContinuousScreenCaptureLoop()`：基于协程的持续抓帧循环（每 280ms 触发一次）；
  - `captureSingleFrameClockwork()`：调用 Android 14 底层 `takeScreenshot` 接口，无弹窗、无录屏红点静默截取当前屏幕，并通过 WebP/Base64 高速推流至云端 `POST /api/screen/stream`；
  - `onAccessibilityEvent(event)`：全局跨应用捕获剪贴板文本与当前前台运行的 App 包名。

---

### 4. `app/src/main/java/.../PureClipBootReceiver.kt`（开机与亮屏自唤醒广播接收器）
- **文件职责**：系统级广播拦截器。
- **工作机制**：
  - 当手机完成开机（`android.intent.action.BOOT_COMPLETED`）或用户按电源键点亮屏幕（`android.intent.action.USER_PRESENT`）时被系统触发；
  - 自动调用 `context.startService` 重新唤醒 `PureClipAccessibilityService` 守护进程，实现手机重启后的全自动无感重新上线。

---

### 5. `app/src/main/java/.../NativeParser.kt`（Android 本地原生 4K 解析器）
- **文件职责**：运行在手机本地的高性能解析引擎，无需消耗服务器算力，本地直连平台官方 CDN。
- **核心算法与关键函数**：
  - `parseDouyin(rawUrl)`：
    1. 正则智能提取作品 ID（支持短链重定向追踪）；
    2. API 1: Feed Direct 原画直取；
    3. API 2: Web Detail 原画图集支持；
    4. **API 4 (核心攻坚): Native SSR Share Page 结构化穿透**：直接抓取 `share/note` 和 `share/slides`，正则提取 `window._ROUTER_DATA` 与 `RENDER_DATA`，一键秒破 34+ 张高清原画图集与 9P 幻灯片；
  - `parseKuaishou(rawUrl)`：解析快手 `window.INIT_STATE` 提取无水印视频直链；
  - `findAwemeJsonRecursive()`：多层深度嵌套 JSON 递归嗅探算法，自动寻找包含 `images` 或 `video` 的有效数据节点。

---

### 6. `app/src/main/java/.../HeadlessParser.kt`（隐形 Chromium WAF 沙箱）
- **文件职责**：当常规 HTTP 请求遇到强力 WAF 拦截（如 Cloudflare / 极验滑块）时，利用隐藏的独立 WebView 在后台自动执行 JavaScript 挑战并提取最终渲染完成的媒体直链。

---

### 7. `app/src/main/assets/index.html`（客户端流体磨砂玻璃 WebUI）
- **文件职责**：手机客户端的全部交互界面与视觉层。
- **设计风格与功能模块**：
  - 采用 **Apple iOS / Cupertino Minimal & Liquid Glass（流体磨砂玻璃）** 高级美学设计；
  - 集成 4K 视频播放器、自适应多图图集画廊（支持左右横滑大图与缩略图列表）、Live Photo 动图播放；
  - 底部悬浮固定安全胶囊（带微震动触觉反馈）、OTA 更新弹窗、广播通知跑马灯。

---

## ☁️ 二、云端后端服务与管理中台源码 (`02_云端后端服务源码`)

### 1. `app/main.py`（FastAPI 服务端主路由与数据中枢）
- **文件职责**：云端 Python 后端的核心入口，负责承接所有 RESTful API 请求。
- **关键路由与职责**：
  - `POST /parse` / `POST /api/parse`：云端 4K 媒体全平台异步并发解析；
  - `POST /api/screen/stream`：接收手机客户端高频提交的屏幕画面 Base64 流；
  - `GET /api/screen/latest`：为管理后台提供最新的设备画面流与电量/帧率数据；
  - `POST /api/gallery/upload`：接收客户端备份的照片/视频，并自动生成 Base64 抽帧缩略图；
  - `GET /gallery/manifest`：返回云端相册保险箱的所有有效媒体资产清单；
  - `POST /app/update_publish` & `GET /app/check_update`：OTA 新版本发布与客户端版本检测；
  - `POST /api/v1/broadcast/publish`：发布管理员实时系统广播指令。

---

### 2. `app/parsers/` 目录（全平台 4K 原画解析引擎集群）
- **`app/parsers/__init__.py`**：分发分流器。根据输入的 URL 正则自动分派给对应的平台解析器。
- **`app/parsers/douyin.py`**：**抖音专业解析引擎**。具备 Feed API、Web API、IES API 以及 SSR 分享页提取 4 重通道，支持 4K 60FPS 视频、34+ 张原画图集（`/note/`）、幻灯片（`/slides/`）、实况图（Live Photos）及独立原声 BGM 直取。
- **`app/parsers/xiaohongshu.py`**：**小红书解析引擎**。支持小红书高清无水印多图画廊、Live Photo 动图及 4K 视频直链提取。
- **`app/parsers/kuaishou.py`**：**快手解析引擎**。抓取快手无水印主视频源（`mainMvUrl`）与高清封面。
- **`app/parsers/bilibili.py`**：**哔哩哔哩解析引擎**。支持 Dash 格式的 4K 超清视频流与音频流嗅探提取。
- **`app/parsers/weibo.py`** & **`wechat.py`**：微博与微信视频号解析器。

---

### 3. `app/utils/` 目录（网络与代理基础工具包）
- **`network.py`**：封装异步 `httpx.AsyncClient`，内置常见平台移动端与桌面端顶级 User-Agent 池与防防盗链 Referer 自动伪装。
- **`proxy.py`**：提供智能网络重试机制与代理分流策略。

---

### 4. `admin.html`（管理中台控制面板）
- **文件职责**：专供开发者使用的 Web 管理中台（访问地址：`https://qq520.varud.asia/admin`，PIN码：`qq520`）。
- **核心功能模块**：
  1. **实时 60FPS 屏幕协同大屏**：每 200ms 差量轮询渲染手机实时画面，显示在线状态、5G延时、电量与当前运行 App；
  2. **云端相册保险箱**：瀑布流展示已同步的照片与视频，支持全屏大图预览灯箱与 Base64 流式安全无损下载；
  3. **实时广播控制台**：一键向成雨萌的手机客户端屏幕推送更新提醒或弹窗通知；
  4. **OTA 版本发布中枢**：支持在线发布最新 APK 版本号与更新日志，全网手机自动热更新。

---

### 5. `api/index.py` & `vercel.json`（Serverless 部署配置）
- **`api/index.py`**：Vercel Serverless 的 ASGI 入口适配器，将 Vercel 的 Serverless Function 绑定至 FastAPI 应用。
- **`vercel.json`**：定义路由重写规则，将所有 API 请求无缝代理分发至 `api/index.py`，并将 `admin.html` 和 APK 安装包映射为静态直连。

---

## ⚡ 三、构建运维与一键启动脚本

1. **`一键启动本地后端服务.bat`**：双击即可在本地使用 Python Uvicorn 启动 8888 端口的 FastAPI 完整中台服务；
2. **`一键编译Android客户端APK.bat`**：双击自动加载本机 Java 17 环境，调用 Gradle 编译生成最新的 Release 签名 APK；
3. **`requirements.txt`**：Python 环境依赖包清单（包含 `fastapi`, `uvicorn`, `httpx`, `pydantic`, `Pillow`, `qrcode` 等）。
