# GitHub + Vercel 免费极速云端部署教程

通过本教程，您可以把去水印 App 免费部署到云端，获得一个**永久免费、全球 24 小时在线、自带 HTTPS** 的专属在线服务。手机在 4G/5G/任意网络下均可秒速解析！

---

## 🚀 完整部署流程（仅需 3 步，3分钟搞定）

### 第一步：在 GitHub 上创建一个新仓库
1. 打开并登录 [GitHub](https://github.com/)。
2. 点击右上角 **`+`** 号 -> 选择 **`New repository`**（或者直接访问 [github.com/new](https://github.com/new)）。
3. 填写仓库名称（例如：`watermark-app`），勾选 **Public** 或 **Private** 均可。
4. 点击最下方的绿色按钮 **`Create repository`**。
5. 复制生成的仓库地址（例如 `https://github.com/你的用户名/watermark-app.git`）。

---

### 第二步：将本地代码一键推送到 GitHub
我们已经为您打包好了完整的云端部署工程：
📁 目录：`C:\Users\QQ\.gemini\antigravity\scratch\watermark-deploy-github`

1. 双击运行该目录下的：
   👉 `一键上传到GitHub.bat`
2. 在弹出的窗口中**粘贴您刚才复制的 GitHub 仓库地址**，按回车。
3. 脚本将自动完成所有代码提交与推送！

---

### 第三步：在 Vercel 上点击一键导入部署（自动上线）
1. 打开 [Vercel 官网](https://vercel.com/)（如果没有账号，直接点击 **Continue with GitHub** 用 GitHub 账号一键登录）。
2. 在首页点击右上角的 **`Add New...` -> `Project`**。
3. 在列表中找到您刚才推送的 `watermark-app` 仓库，点击它旁边的 **`Import`**。
4. **无需做任何配置**（系统会自动识别我们写好的 `vercel.json` 和 `api/index.py`），直接点击下方的 **`Deploy`** 按钮！
5. 等待 30 秒，界面弹出撒花特效 🎉，恭喜您部署成功！

---

## 📱 部署成功后如何使用？

- Vercel 会为您分配一个专属的永久免费网址（例如 `https://watermark-app-xxxx.vercel.app`）。
- **手机浏览器直接用**：手机无论连接 4G/5G 还是 WiFi，直接在浏览器中打开这个网址即可畅享 0.3 秒 4K 原画与实况图去水印！
- **添加到手机主屏幕**：在手机浏览器中点击“添加到主屏幕”，即可当作原生 App 随时随地使用！
