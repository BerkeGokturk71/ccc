import logging
import socketio
import requests
import re
import engineio.packet
import os
import threading
import time
import urllib3
from dotenv import load_dotenv
from telegram_bot import telegram_gonder
from hareketler import oyun_verisini_cozumle
import database  # Flask ile veri paylaşımı için

# --- AYARLAR ---
load_dotenv()
KADI = os.getenv("KADI")
SIFRE = os.getenv("SIFRE")
BASE_URL = os.getenv("BASE_URL")
SOCKET_URL = os.getenv("SOCKET_URL")
SERVER = os.getenv("SERVER", "Veda")

# --- ENGINE.IO PATCH ---
original_decode = engineio.packet.Packet.decode
def patched_decode(self, encoded_packet):
    try:
        clean_data = re.sub(r'^\d+:', '', encoded_packet)
        return original_decode(self, clean_data)
    except Exception:
        return original_decode(self, encoded_packet)

engineio.packet.Packet.decode = patched_decode
logging.basicConfig(level=logging.ERROR)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
gonderilen_bildirimler = []
# --- SESSION VE LOGIN ---
session = requests.Session()
session.verify = False
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/oyun/{SERVER}"
}

def login():
    print("🔑 LOGIN işlemleri başlatılıyor...")
    session.post(f"{BASE_URL}/app/ajax/giris/login.php", data={"kadi": KADI, "sifre": SIFRE}, headers=headers,verify=False)
    session.post(f"{BASE_URL}/app/ajax/giris/sw_sec.php", data={"sw_url": SERVER}, headers=headers,verify=False)
    session.get(f"{BASE_URL}/sunucular", headers=headers)
    session.post(f"{BASE_URL}/app/ajax/kullanici.php", data={"sayfa_yeri": "oyun"}, headers=headers,verify=False)
    print("✅ LOGIN tamamlandı.")

# --- TAZELEME MOTORU (YENİ EKLEDİĞİMİZ KISIM) ---
def refresh_data_periodically():
    """
    30 saniyede bir socket bağlantısını koparıp tekrar bağlanır.
    Bu sayede sunucu her seferinde 'ilk_giris' verisini tekrar gönderir.
    """
    print("🔄 Otomatik Reconnect Motoru Aktif (30sn aralıkla).")
    
    while True:
        time.sleep(30) # 30 saniye bekle
        try:
            if sio.connected:
                print("🔌 Veri tazeleme için bağlantı sıfırlanıyor...")
                sio.disconnect() # Bağlantıyı kes
            
            # Kısa bir bekleme (sunucunun bağlantının koptuğunu anlaması için)
            time.sleep(2)
            
            # Tekrar bağlan (Login fonksiyonunu tekrar çağırmaya gerek yok, çerezler session'da duruyor)
            sio.connect(
                SOCKET_URL,
                headers={"Origin": BASE_URL, "Referer": f"{BASE_URL}/oyun/{SERVER}"},
                socketio_path="/socket.io",
                transports=["polling", "websocket"]
            )
            print("📡 Yeniden bağlandı, güncel veriler bekleniyor...")

        except Exception as e:
            print(f"⚠️ Reconnect Hatası: {e}")
            # Hata alırsa login'i tekrar dene (çerezler patlamış olabilir)
            try:
                login()
            except:
                pass

# --- SOCKET.IO ---
sio = socketio.Client(http_session=session, ssl_verify=False,
                    request_timeout=120, reconnection=True,
                    reconnection_attempts=0, reconnection_delay=1,
                    logger=False, engineio_logger=False)

@sio.on('ilk_giris')
def on_ilk_giris(data):
    global gonderilen_bildirimler # Listeye dışarıdan erişmek için şart
    
    sonuclar = oyun_verisini_cozumle(data)
    if not sonuclar:
        return

    # Flask veritabanını güncelle
    database.update_moves(sonuclar)

    # --- TELEGRAM BİLDİRİM MANTIĞI ---
    for h in sonuclar:
        # Sadece Ticaretleri ve içinde kılıç/zırh geçenleri ayıkla
        if "TİCARET" in h['tip']:
            icerik = h['miktar'].lower()
            if "zirh" in icerik or "kilic" in icerik or "zırh" in icerik:
                
                # BENZERSİZ ANAHTAR: Aynı gönderen ve aynı varış saati gelirse bildirim atma
                hareket_key = f"{h['gonderen']}_{h['varis']}"
                
                if hareket_key not in gonderilen_bildirimler:
                    mesaj = (
                        f"🛡️ **KRİTİK SEVKİYAT TESPİT EDİLDİ!**\n\n"
                        f"👤 Kimden: {h['gonderen']}\n"
                        f"🎯 Kime: {h['hedef']}\n"
                        f"📦 Ne Gidiyor: {h['miktar']}\n"
                        f"⏰ Varış: {h['varis']}"
                    )
                    
                    telegram_gonder(mesaj) # Botu ateşle
                    
                    # Bildirimi listeye ekle ki 30 saniye sonra tekrar atmasın
                    gonderilen_bildirimler.append(hareket_key)
                    
                    # Listenin şişmesini önle (Son 50 kayıt kalsın)
                    if len(gonderilen_bildirimler) > 50:
                        gonderilen_bildirimler.pop(0)
                    
                    print(f"📱 Bildirim gönderildi: {h['gonderen']} -> {h['miktar']}")

    print(f"🚀 Radar Güncellendi: {len(sonuclar)} hareket aktif.")

# --- ANA BAŞLATICI ---
def start_socket_engine():
    login()
    
    # 1. HTTP Tazeleyiciyi ayrı bir thread'de başlat
    refresh_thread = threading.Thread(target=refresh_data_periodically, daemon=True)
    refresh_thread.start()
    
    # 2. Socket bağlantısını başlat
    try:
        sio.connect(
            SOCKET_URL,
            headers={"Origin": BASE_URL, "Referer": f"{BASE_URL}/oyun/{SERVER}"},
            socketio_path="/socket.io",
            transports=["polling", "websocket"]
        )
        sio.wait()
    except Exception as e:
        print(f"💥 Socket Hatası: {e}")