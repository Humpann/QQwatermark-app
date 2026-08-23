# OmniMedia Pro - GitHub Upload Script
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       OmniMedia Pro - GitHub 仓库一键上传工具           " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$repoUrl = Read-Host "请输入您的 GitHub 仓库地址 (例如 https://github.com/yourname/watermark-app.git)"
$repoUrl = $repoUrl.Trim()

if ([string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Host "错误：未输入任何 GitHub 地址！" -ForegroundColor Red
    exit 1
}

Write-Host "`n正在检查并初始化 Git 仓库..." -ForegroundColor Yellow

# Ensure git is initialized
if (-not (Test-Path ".git")) {
    git init
}

# Set default git config if missing
$gitName = git config user.name
if ([string]::IsNullOrWhiteSpace($gitName)) {
    git config user.name "OmniMedia"
    git config user.email "omnimedia@example.com"
}

Write-Host "正在暂存文件并创建提交..." -ForegroundColor Yellow
git add .
git commit -m "Deploy OmniMedia Pro to Vercel/Cloud" 2>$null

Write-Host "正在配置远程仓库并推送到 GitHub..." -ForegroundColor Yellow
git branch -M main
git remote remove origin 2>$null
git remote add origin $repoUrl

Write-Host "正在执行 git push (如果弹出登录窗口，请在浏览器中授权)..." -ForegroundColor Cyan
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host " 🎉 恭喜！代码已成功推送到您的 GitHub 仓库！" -ForegroundColor Green
    Write-Host " 现在您可以打开 https://vercel.com 点击 Import 即可一键上线！" -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "推送失败，请检查网络或 GitHub 登录凭证。" -ForegroundColor Red
}
