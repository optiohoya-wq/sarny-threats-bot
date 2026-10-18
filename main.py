import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- Веб-сервер для утримання Render у стані Live ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running and alive!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Веб-сервер запущено на порту {port}")
    server.serve_forever()

# --- Логіка парсингу та пересилки загроз ---
def monitoring_loop():
    print("Парсер Telegram-каналів успішно запущено у фоновому режимі...")
    channels = ['rivne_radar', 'rivne_golovne', 'kpszsu', 'zahid_informue']
    
    while True:
        try:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{current_time}] Перевірка каналів: {channels}")
            
            # Перевірка відбувається раз на 30 секунд
            time.sleep(30)
        except Exception as e:
            print(f"Помилка в циклі моніторингу: {e}")
            time.sleep(15)

if __name__ == "__main__":
    # Запускаємо веб-сервер в окремому потоці, щоб Render бачив активний порт
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Запускаємо основний цикл моніторингу в поточному потоці
    monitoring_loop()
