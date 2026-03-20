import os
from flask import Flask

app = Flask(__name__)

def run_flask():
    # BURASI KRİTİK: Koyeb portu "PORT" değişkeniyle yollar.
    # Eğer 5000 yazarsan Koyeb "kapı kapalı" der ve uygulamayı kapatır.
    port = int(os.environ.get("PORT", 8000))
    
    # host mutlaka '0.0.0.0' olmalı. 'localhost' dersen dışarıya kapanır.
    app.run(host='0.0.0.0', port=port)