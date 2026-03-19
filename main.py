import os
import threading

from flask import app
from socket_engine import start_socket_engine
from web_app import run_flask

if __name__ == '__main__':
    # Önce botu başlatıyoruz ama thread olarak
    print("🤖 Bot thread'i hazırlanıyor...")
    t = threading.Thread(target=start_socket_engine, daemon=True)
    t.start()
    
    # Sonra Flask'ı Render'ın istediği portta açıyoruz
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Flask {port} portunda açılıyor...")
    app.run(host='0.0.0.0', port=port, debug=False)