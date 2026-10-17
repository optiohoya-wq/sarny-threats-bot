import time
import requests
from bs4 import BeautifulSoup

CHANNELS = ['rivne_radar', 'rivne_golovne', 'kpszsu', 'zahid_informue']
WEBHOOK_URL = 'https://sarny-threats.optio-hoya.workers.dev'

seen_messages = set()

def check_channels():
    for channel in CHANNELS:
        url = f'https://t.me/s/{channel}'
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.find_all('div', class_='tgme_widget_message')
            
            for post in posts:
                post_id = post.get('data-post')
                if not post_id or post_id in seen_messages:
                    continue
                
                text_elem = post.find('div', class_='tgme_widget_message_text')
                text = text_elem.get_text(separator='\n') if text_elem else ""
                
                seen_messages.add(post_id)
                
                payload = {
                    "channel": channel,
                    "post_id": post_id,
                    "text": text
                }
                
                requests.post(WEBHOOK_URL, json=payload, timeout=5)
                print(f"New post from {channel}: {post_id}")
                
        except Exception as e:
            print(f"Error checking {channel}: {e}")

if __name__ == '__main__':
    print("Parser started!")
    while True:
        if len(seen_messages) > 1000:
            seen_messages.clear()
        check_channels()
        time.sleep(30)
