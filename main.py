import os
import sys
import asyncio
import requests
from telethon import TelegramClient, events
from aiohttp import web

# Примусово вимикаємо буферизацію логів
sys.stdout.reconfigure(line_buffering=True)

API_ID = int(os.environ.get("API_ID") or os.environ.get("TELEGRAM_API_ID", 0))
API_HASH = os.environ.get("API_HASH") or os.environ.get("TELEGRAM_API_HASH", "")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") or os.environ.get("CLOUDFLARE_WEBHOOK_URL", "")

CHANNELS = ['rivne_radar', 'rivne_golovne', 'kpszsu', 'zahid_informue']

# 1. Легкий веб-сервер на аіохттп для підтримки статусу Live на Render
async def handle_ping(request):
    return web.Response(text="Bot and Telethon client are active.")

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

async def main():
    print("=== Запуск комбінованого сервісу Telethon + Web ==[span_1](start_span)[span_1](end_span)")
    
    if not BOT_TOKEN:
        print("[Error] TELEGRAM_BOT_TOKEN не задано!")
        return

    # Ініціалізація Telegram клієнта
    client = TelegramClient('sarny_bot_session', API_ID, API_HASH)

    @client.on(events.NewMessage(chats=CHANNELS))
    async def handler(event):
        chat = await event.get_chat()
        channel_name = getattr(chat, 'username', chat.title)
        message_text = event.raw_text
        print(f"[New Message] З каналу @{channel_name}: {message_text[:50]}...")
        send_to_cloudflare(channel_name, message_text)

    print(f"[Telethon] Підключення до Telegram та моніторинг: {CHANNELS}")
    await client.start(bot_token=BOT_TOKEN)

    # Запускаємо вебсервер у тому ж асинхронному циклі, щоб Render бачив порт
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[Web] Вебсервер успішно працює на порту {port}")

д# Працюємо безперервно
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
