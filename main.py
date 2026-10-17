import os
import requests
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://sarny-threats.optio-hoya.workers.dev")

CHANNELS = ['rivne_radar', 'rivne_golovne', 'kpszsu', 'zahid_informue']

client = TelegramClient('sarny_session', API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHANNELS))
async def handler(event):
    if event.message and event.message.text:
        payload = {
            "channel_post": {
                "text": event.message.text
            }
        }
        try:
            requests.post(WEBHOOK_URL, json=payload, timeout=5)
            print(f"Переслано: {event.message.text[:30]}...")
        except Exception as e:
            print(f"Помилка відправки: {e}")

print("Скрипт моніторингу загроз запущено...")
client.start()
client.run_until_disconnected()
