# NSFC Report Downloader / 国基报告下载器

[English](#english) | [中文](#中文)

---

## English

### Introduction
A lightweight tool to download publicly available project reports from the **National Natural Science Foundation of China (NSFC)**.  
It automatically saves each page as an image and merges them into a single PDF file for offline reading and research.

The program **only simulates normal human browsing** with built‑in delays. It does **not** bypass any login, CAPTCHA, IP blocking, or other security measures. It respects `robots.txt` and is intended for **personal academic use only**.

### Features
- Download full‑text reports from NSFC public pages
- Convert multiple page images into a single PDF
- Built‑in random delays to avoid overloading the source server
- No authentication or anti‑crawler circumvention

### Requirements
- Python 3.7+
- Packages: `requests`, `Pillow`, `img2pdf` (or `fpdf`)

### Installation
```bash
git clone https://github.com/YourUsername/NSFC-Report-Downloader.git
cd NSFC-Report-Downloader
pip install -r requirements.txt
