import os
import time
import requests
import threading
from bs4 import BeautifulSoup
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. ВЕБ-СЕРВЕР ДЛЯ RENDER HEALTH CHECK ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - Bot is running")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Web server started on port {port}")
    server.serve_forever()

# Запускаємо сервер у фоновому потоці
threading.Thread(target=run_web_server, daemon=True).start()

# --- 2. НАЛАШТУВАННЯ ПАРСЕРА TELEGRAM ---
CHANNELS = ["rivne_radar", "rivne_golovne", "kpszsu", "zahid_informue"]
CLOUDFLARE_WEBHOOK = "https://sarny-threats.optio-hoya.workers.dev"

# Словник для збереження останніх відправлених ID постів
last_seen_ids = {channel: None for channel in CHANNELS}

def check_channel(channel):
    url = f"https://t.me/s/{channel}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[{channel}] Помилка завантаження: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        posts = soup.find_all("div", class_="tgme_widget_message")
        
        if not posts:
            return

        last_post = posts[-1]
        post_id = last_post.get("data-post")
        
        if not post_id:
            return

        # Перевіряємо, чи це новий пост
        if last_seen_ids[channel] is None:
            last_seen_ids[channel] = post_id
            print(f"[{channel}] Ініціалізовано. Останній пост: {post_id}")
            return

        if post_id != last_seen_ids[channel]:
            last_seen_ids[channel] = post_id
            
            # Отримуємо текст поста
            text_div = last_post.find("div", class_="tgme_widget_message_text")
            text = text_div.get_text(separator="\n").strip() if text_div else ""
            
            print(f"[{channel}] Новий пост {post_id}! Відправляємо на Cloudflare...")
            
            # Відправляємо на вебхук
            payload = {
                "channel": channel,
                "post_id": post_id,
                "text": text,
                "link": f"https://t.me/{post_id}"
            }
            
            try:
                res = requests.post(CLOUDFLARE_WEBHOOK, json=payload, timeout=10)
                print(f"[{channel}] Відповідь вебхука: {res.status_code}")
            except Exception as e:
                print(f"[{channel}] Помилка відправки на вебхук: {e}")

    except Exception as e:
        print(f"[{channel}] Помилка парсингу: {e}")

# --- 3. ГОЛОВНИЙ ЦИКЛ РОБОТИ ---
if __name__ == "__main__":
    print("Парсер запущенiй і готовий до роботи!")
    while True:
        for channel in CHANNELS:
            check_channel(channel)
            time.sleep(2)  # Невеличка пауза між каналами
        time.sleep(30)  # Перевірка кожні 30 секунд
