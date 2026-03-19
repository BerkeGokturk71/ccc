import threading
from socket_engine import start_socket_engine
from web_app import run_flask

if __name__ == "__main__":
    # 1. Arka planda Socket'i başlat
    socket_thread = threading.Thread(target=start_socket_engine, daemon=True)
    socket_thread.start()

    # 2. Flask'ı ana thread'de başlat
    print("🌐 Flask sunucusu http://localhost:5000 adresinde başlatılıyor...")
    run_flask()