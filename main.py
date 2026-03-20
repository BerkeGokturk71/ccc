import os
import threading

from flask import app
from socket_engine import start_socket_engine
from web_app import run_flask

if __name__ == "__main__":
   def run_flask():
    # Koyeb'in verdiği portu al, yoksa 8000 kullan
    port = int(os.environ.get("PORT", 8000)) 
    app.run(host='0.0.0.0', port=port)