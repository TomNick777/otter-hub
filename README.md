# 🦦 otter-hub

> 海獭数字洞穴 · 统一入口管理你的生活

基于 **GitHub Gist** 的本地优先数据同步，所有数据存储在你的私人 Gist 中，完全私有。

## 🚀 快速开始

1. 访问 https://github.com/settings/tokens/new 创建 Personal Access Token
2. 勾选 **Gist** 权限
3. 打开 `index.html`，粘贴 Token 即可登录

## 📱 应用矩阵

| 文件 | 功能 |
|------|------|
| `index.html` | 🏠 **默认首页** — 新标签页导航 + 时钟 |
| `app-todo.html` | 📋 待办清单 — 多清单 + 优先级 + 截止日期 |
| `app-habits.html` | 🎯 习惯打卡 — 日历视图 + 连续天数 + 周统计 |
| `app-ledger.html` | 💰 个人账本 — 收支记录 + 月度统计 |
| `app-dashboard.html` | 📊 数据仪表盘 — 聚合所有应用数据 |

## 🏗️ 技术架构

- **前端**: 原生 HTML/CSS/JS，零依赖
- **数据存储**: GitHub Gist API（私有）
- **同步**: 单 Gist 文件（`otter-unified.json`）
- **部署**: GitHub Pages（每个 app 独立 URL）
- **主题**: 深色 Bento Grid，珊瑚/鼠尾草/海洋三色点缀

## 📁 文件结构

```
otter-hub/
├── index.html          ← 🏠 默认首页（新标签页）
├── app-dashboard.html  ← 📊 数据仪表盘
├── app-todo.html       ← 📋 待办清单
├── app-habits.html     ← 🎯 习惯打卡
├── app-ledger.html     ← 💰 个人账本
├── css/
│   └── unified.css     ← 共享设计系统
├── js/
│   └── core.js         ← 统一认证 + Gist 同步引擎
├── setup.ps1           ← 部署脚本（PowerShell）
└── README.md
```

## 🔑 数据结构

所有数据存储在单一 Gist 文件 `otter-unified.json`：

```json
{
  "version": "2.0.0",
  "lastUpdated": 1745123456789,
  "todo":  { "lists": [], "tasks": [] },
  "habits": { "habits": [], "checkins": {} },
  "ledger": { "records": [], "categories": {} },
  "homepage": { "shortcuts": [] }
}
```

## 🔒 隐私说明

- 所有数据存储在你的 **私人 GitHub Gist** 中
- Token 仅用于 Gist 读写，不获取任何仓库权限
- 多设备同步：同一 Token，即时同步

## 🎨 设计系统

| Token | 值 |
|-------|-----|
| 背景 | `#08090C` |
| 卡片 | `rgba(255,255,255,0.035)` |
| 珊瑚 | `#FF6B5B` |
| 鼠尾草 | `#7EC8A3` |
| 海洋 | `#5BC4CF` |
| 字体 | Instrument Serif + Space Grotesk |

## ⚙️ 部署

推送 `main` 分支后，GitHub Actions 自动部署到 GitHub Pages。

---

🦪 *一只海獭管理你的数字生活*
