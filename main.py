import os
import sys
import asyncio
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events

sys.stdout.reconfigure(line_buffering=True)

# Отримуємо значення за вашими назвами з Render
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

CHANNELS = ['rivne_radar', 'rivne_golovne', 'kpszsu', 'zahid_informue']

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot and Telethon client are active.")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"[Web] Сервер перевірки стану запущено на порту {port}")
    server.serve_forever()

def send_to_cloudflare(channel, text):
    if not WEBHOOK_URL:
        print("[Webhook Error] WEBHOOK_URL не налаштовано!")
        return
    payload = {
        "channel": channel,
        "text": text
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"[Webhook] Відправлено з каналу '{channel}'. Статус: {response.status_code}")
    except Exception as e:
        print(f"[Webhook Error] Помилка відправки: {e}")

async def start_telegram_monitoring():
    print("[Telethon] Ініціалізація Telegram клієнта...")
    
    client = TelegramClient('sarny_bot_session', API_ID, API_HASH)

    @client.on(events.NewMessage(chats=CHANNELS))
    async def handler(event):
        chat = await event.get_chat()
        channel_name = getattr(chat, 'username', chat.title)
        message_text = event.raw_text
        print(f"[New Message] З каналу @{channel_name}: {message_text[:50]}...")
        
        send_to_cloudflare(channel_name, message_text)

    print(f"[Telethon] Запуск моніторингу каналів: {CHANNELS}")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    print("=== Запуск системи моніторингу та пересилки ===")
    
    web_thread = threading.Thread(target=run_health_server, daemon=True)
    web_thread.start()

    try:
        asyncio.run(start_telegram_monitoring())
    except Exception as err:
        print(f"[Fatal Error] Помилка виконання: {err}")
