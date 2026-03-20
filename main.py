import threading
import time

from socket_engine import start_socket_engine
from web_app import run_flask


if __name__ == "__main__":
    # 1. Arka planda Socket'i başlat
    socket_thread = threading.Thread(target=start_socket_engine, daemon=True)
    socket_thread.start()

    # 2. Flask'ı başlat
    print("🌐 Flask sunucusu başlatılıyor...")
    try:
        run_flask()
    except Exception as e:
        print(f"❌ Flask başlatılamadı: {e}")
    
    # Flask kapansa bile (Code 0 almamak için) ana thread'i canlı tut
    while True:
        time.sleep(10)