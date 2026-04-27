import os
import sys
import re
import time
import glob
import random
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs
from typing import Union, Tuple
import requests
from PIL import Image

MAX_RETRIES = 10
DELAY_BETWEEN_PAGES = (1.5, 3.0)
TIMEOUT = 60
HOST = "https://kd.nsfc.cn"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/x-www-form-urlencoded",
    "Connection": "close",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


class DownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("国基报告批量下载工具")
        self.root.geometry("900x700")

        self.is_running = False
        self.current_futures = []

        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="下载链接 (逗号分号分隔，不分中英文)", padding=10)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.url_text = scrolledtext.ScrolledText(input_frame, height=15, wrap=tk.WORD)
        self.url_text.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill="x", padx=10, pady=5)

        worker_frame = ttk.Frame(btn_frame)
        worker_frame.pack(side="left", padx=5)

        ttk.Label(worker_frame, text="并发下载数量最多为3，太多服务器报错:").pack(side="left", padx=(0, 5))
        self.worker_var = tk.StringVar(value="3")
        self.worker_combo = ttk.Combobox(worker_frame, textvariable=self.worker_var,
                                         values=[str(i) for i in range(1, 4)],
                                         width=5, state="readonly")
        self.worker_combo.pack(side="left")

        self.start_btn = ttk.Button(btn_frame, text="开始下载", command=self.start_download)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_download, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        output_frame = ttk.LabelFrame(self.root, text="下载进度", padding=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=20, wrap=tk.WORD, state='disabled')
        self.output_text.pack(fill="both", expand=True)

    def log(self, message):
        self.output_text.config(state='normal')
        self.output_text.insert('end', message + '\n')
        self.output_text.see('end')
        self.output_text.config(state='disabled')

    def parse_urls(self):
        url_text = self.url_text.get('1.0', 'end').strip()
        if not url_text:
            return []
        separators = [',', '，', ';', '；', '\n']
        urls = [url_text]
        for sep in separators:
            new_urls = []
            for url in urls:
                new_urls.extend([u.strip() for u in url.split(sep) if u.strip()])
            urls = new_urls
        return urls

    def stop_download(self):
        self.log("\n⚠ 正在停止所有下载任务...")
        self.is_running = False

    def disable_controls(self):
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.url_text.config(state='disabled')
        self.worker_combo.config(state="disabled")

    def enable_controls(self):
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.url_text.config(state='normal')
        self.worker_combo.config(state="readonly")

    # ===================== 核心下载逻辑 =====================
    @staticmethod
    def extract_project_id(url_or_id: str) -> str:
        if url_or_id.startswith("http"):
            parsed = urlparse(url_or_id)
            params = parse_qs(parsed.query)
            if "id" in params:
                return params["id"][0]
            raise ValueError(f"URL 中未找到 id 参数：{url_or_id}")
        cleaned = url_or_id.strip()
        if re.match(r'^[a-f0-9]{32}$', cleaned):
            return cleaned
        raise ValueError(f"无效的项目 ID: {cleaned}")

    @staticmethod
    def get_project_info(project_id: str) -> dict:
        url = f"{HOST}/api/baseQuery/conclusionProjectInfo/{project_id}"
        resp = requests.post(url, headers=HEADERS, timeout=TIMEOUT)
        data = resp.json()
        if data.get("code") != 200:
            raise RuntimeError(f"获取项目信息失败：{data}")
        info = data["data"]
        return {
            "name": info.get("projectName", "未知项目"),
            "admin": info.get("projectAdmin", ""),
            "unit": info.get("dependUnit", ""),
            "ratify_no": info.get("ratifyNo", ""),
        }

    @staticmethod
    def download_page(project_id: str, index: int) -> Tuple[Union[bytes, None], str]:
        api_url = f"{HOST}/api/baseQuery/completeProjectReport"
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = requests.post(api_url, headers=HEADERS, data=f"id={project_id}&index={index}", timeout=TIMEOUT)
                data = resp.json()
                if data.get("code") != 200 or not data.get("data", {}).get("url"):
                    continue
                img_url = HOST + data["data"]["url"]
                img_resp = requests.get(img_url, headers={"user-agent": HEADERS["user-agent"]}, timeout=TIMEOUT)
                if img_resp.status_code == 200:
                    header_bytes = img_resp.content[:4]
                    ext = ".png" if header_bytes[:4] == b'\x89PNG' else ".jpg"
                    return img_resp.content, ext
            except:
                time.sleep(1)
        return None, ""

    @staticmethod
    def images_to_pdf(image_dir: str, output_pdf: str):
        patterns = [os.path.join(image_dir, f"page_*.{ext}") for ext in ("png", "jpg")]
        image_files = sorted(f for p in patterns for f in glob.glob(p))
        if not image_files:
            raise FileNotFoundError(f"目录中未找到图片：{image_dir}")
        images = [Image.open(f).convert("RGB") for f in image_files]
        images[0].save(output_pdf, "PDF", resolution=150.0, save_all=True, append_images=images[1:])
        size_mb = os.path.getsize(output_pdf) / (1024 * 1024)
        return size_mb

    def download_project(self, url: str, base_dir: str):
        project_id = self.extract_project_id(url)
        info = self.get_project_info(project_id)
        safe_name = re.sub(r'[/\\?%*:|"<>]', '-', info['name'])
        image_dir = os.path.join(base_dir, f"结题报告_{info['ratify_no']}")
        os.makedirs(image_dir, exist_ok=True)

        index = 1
        total_downloaded = 0
        while self.is_running:
            existing_files = glob.glob(os.path.join(image_dir, f"page_{index:03d}.*"))
            if existing_files:
                index += 1
                continue
            self.log(f"\n【{info['name']}】正在下载第 {index} 页...")
            content, ext = self.download_page(project_id, index)
            if content is None:
                break
            filepath = os.path.join(image_dir, f"page_{index:03d}{ext}")
            with open(filepath, "wb") as f:
                f.write(content)
            self.log(f"  ✓ 第 {index} 页下载完成 ({len(content) / 1024:.1f} KB)")
            total_downloaded += 1
            index += 1
            time.sleep(random.uniform(*DELAY_BETWEEN_PAGES))

        if self.is_running:  # 只有下载完成才生成 PDF
            pdf_path = os.path.join(base_dir, f"结题报告_{info['ratify_no']}_{safe_name}.pdf")
            size_mb = self.images_to_pdf(image_dir, pdf_path)
            self.log(f"\n🎉 {info['name']} PDF 已生成：{pdf_path} ({size_mb:.1f} MB)")

        return total_downloaded

    # ===================== 并发下载 =====================
    def run_one(self, i, total, url):
        if not self.is_running:
            return False
        try:
            self.log(f"\n【任务 {i}/{total}】开始处理: {url}")
            self.download_project(url, ".")
            return True
        except Exception as e:
            self.log(f"✗ 【任务 {i}/{total}】失败：{e}")
            return False

    def download_task(self, urls, max_workers):
        self.log(f"开始批量下载，共 {len(urls)} 个链接，并发数量：{max_workers}")
        self.log("="*70)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.run_one, i, len(urls), url): url for i, url in enumerate(urls, 1)}
            completed = 0
            success = 0
            for future in as_completed(futures):
                if not self.is_running:
                    break
                completed += 1
                if future.result():
                    success += 1
                self.log(f"\n[总体进度] 已完成：{completed}/{len(urls)} (成功：{success})")
        self.is_running = False
        self.root.after(0, self.enable_controls)
        self.log("\n批量下载任务结束！")


    def start_download(self):
        urls = self.parse_urls()
        if not urls:
            self.log("错误：请在链接输入框中添加要下载的链接")
            return
        max_workers = int(self.worker_var.get())
        self.is_running = True
        self.disable_controls()
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.config(state='disabled')
        threading.Thread(target=self.download_task, args=(urls, max_workers), daemon=True).start()


def main():
    root = tk.Tk()
    app = DownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
