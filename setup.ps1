# otter-hub 部署脚本
# 运行方式: 右键 -> 用 PowerShell 运行

$ErrorActionPreference = "Stop"
$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "🦦 otter-hub 部署脚本" -ForegroundColor Cyan
Write-Host "=" * 40

# 1. 检查 GitHub CLI
Write-Host "`n[1/5] 检查 GitHub CLI..." -ForegroundColor Yellow
$ghVersion = gh --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ GitHub CLI 未安装或未登录" -ForegroundColor Red
    Write-Host "请运行: gh auth login" -ForegroundColor Yellow
    Write-Host "或手动在 GitHub 创建仓库后运行本脚本" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ $ghVersion"

# 2. Git 初始化
Write-Host "`n[2/5] Git 初始化..." -ForegroundColor Yellow
Set-Location $repoDir
git init
git add .
git commit -m "🦦 otter-hub v2.0 - 统一全家桶

- 统一设计系统 (Bento Grid, 珊瑚/鼠尾草/海洋三色)
- 核心: js/core.js (统一认证 + Gist 同步引擎)
- app-home.html  - 主页导航 (时钟 + 快捷方式)
- app-todo.html  - 待办清单 (多清单 + 优先级)
- app-habits.html - 习惯打卡 (日历 + 连续天数)
- app-ledger.html - 个人账本 (收支 + 月度统计)
- index.html     - 仪表盘 (数据聚合视图)
- 统一 Gist (otter-unified.json) 数据存储"
Write-Host "✅ Git 提交完成"

# 3. 创建 GitHub 仓库
Write-Host "`n[3/5] 创建 GitHub 仓库..." -ForegroundColor Yellow
gh repo create otter-hub --public --source=. --remote=origin --push 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "仓库可能已存在，尝试推送..." -ForegroundColor Yellow
    git branch -M main
    $remote = git remote get-url origin 2>$null
    if (-not $remote) {
        Write-Host "❌ 无法确定远程仓库" -ForegroundColor Red
        Write-Host "请手动创建 GitHub 仓库后运行: git push -u origin main" -ForegroundColor Yellow
        exit 1
    }
    git push -u origin main 2>$null
}
Write-Host "✅ 仓库创建/推送完成"

# 4. 启用 GitHub Pages
Write-Host "`n[4/5] 启用 GitHub Pages..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
gh repo pages --source branch=main --dir=/ 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ GitHub Pages 可能需要手动启用" -ForegroundColor Yellow
    Write-Host "请访问: https://github.com/TomNick777/otter-hub/settings/pages" -ForegroundColor Yellow
    Write-Host "选择: Source -> Deploy from a branch -> main -> / (root)" -ForegroundColor Yellow
} else {
    Write-Host "✅ GitHub Pages 已启用"
}

# 5. 完成
Write-Host "`n[5/5] 完成！" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 你的应用将部署到:" -ForegroundColor Cyan
Write-Host "  🏠 主页:  https://tomnick777.github.io/otter-hub/app-home.html" -ForegroundColor White
Write-Host "  📋 待办:  https://tomnick777.github.io/otter-hub/app-todo.html" -ForegroundColor White
Write-Host "  🎯 打卡:  https://tomnick777.github.io/otter-hub/app-habits.html" -ForegroundColor White
Write-Host "  💰 账本:  https://tomnick777.github.io/otter-hub/app-ledger.html" -ForegroundColor White
Write-Host "  📊 仪表盘: https://tomnick777.github.io/otter-hub/" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  GitHub Pages 部署需要 1-2 分钟" -ForegroundColor Yellow
Write-Host ""
Write-Host "🦪 享受你的海獭全家桶！" -ForegroundColor Cyan
