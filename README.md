# NSFC Report Downloader / 国基报告下载

### Introduction
A lightweight tool to download publicly available project reports from the **National Natural Science Foundation of China (NSFC)**.  
It automatically saves each page as an image and merges them into a single PDF file for offline reading and research.

The program **only simulates normal human browsing** with built‑in delays. It does **not** bypass any login, CAPTCHA, IP blocking, or other security measures. It respects `robots.txt` and is intended for **personal academic use only**.

### Features
- Download full‑text reports from NSFC public pages
- Convert multiple page images into a single PDF
- Built‑in random delays to avoid overloading the source server
- No authentication or anti‑crawler circumvention

---

## 简介
一个轻量级工具，用于下载国家自然科学基金（NSFC）官网公开可见的项目报告。  
程序自动将每一页保存为图片，并合并成一个 PDF 文件，方便离线阅读和学术研究。

本工具**仅模拟正常人工浏览行为**，内置请求延迟，不绕过任何登录、验证码、IP封锁或其他安全措施，遵守 `robots.txt`，**仅供个人学术使用**。

## 功能
- 批量下载国基公开报告的完整页面
- 将多页图片自动转换为一个 PDF 文件
- 内置随机/固定延迟，避免对源服务器造成过大压力
- 无需认证，不突破任何反爬机制
## 📥 获取软件

- **代码版**：克隆本仓库，安装依赖后运行 `python main.py`。
- **EXE版**：前往右侧 [Releases](https://github.com/BruceQ1/NSFC-Report-Downloader/releases/tag/v1.1.0) 页面下载最新版 `NSFC_Downloader.exe`，**无需安装 Python**，双击即可运行。

## 🚀 快速上手

1. 打开软件，在输入框中粘贴**一个或多个**国基报告详情页的链接。
   - 支持逗号（中英文均可）、分号、换行分隔多个链接。
   - 示例：`https://kd.nsfc.cn/xxxx?id=abc123` 或直接使用32位项目ID。
2. **并发下载数量最多为3，太多服务器报错** → 下拉框选择并发数（1~3），默认3。
3. 点击「开始下载」，程序会自动：
   - 提取项目信息（名称、编号、依托单位等）
   - 逐页下载报告图片（内置1.5~3秒随机延迟，避免封IP）
   - 将图片合并为一份PDF，保存到软件所在目录下的 `结题报告_项目编号_项目名称.pdf`
4. 点击「停止」可安全中断任务（已下载的图片仍会合并为PDF）。

## ⚠️ 注意事项

- **并发数严禁超过3**，过高并发会导致服务器拒绝服务，程序本身也已强制限制选项最大为3。
- 请勿短时间内大批量启动任务，**建议配合使用**：每次下载后稍等几秒再开始下一批。
- 本工具仅用于**个人学术研究**，下载内容版权归原作者或国基所有，**禁止商用或二次分发**。
- 若下载中断，重新运行程序时，**已存在的页面不会重复下载**，会继续下载剩余页。
