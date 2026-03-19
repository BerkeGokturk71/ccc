from datetime import datetime

def oyun_verisini_cozumle(data):
    hareketler = []
    vals = data.get('vals', {})
    
    for v_id, icerik in vals.items():
        # İşlenecek kategoriler
        kategoriler = {
            'mal_gonder': '📦 TİCARET',
            'saldiri': '⚔️ SALDIRI',
            'toplama': '⛏️ TOPLAMA'
        }

        for anahtar, tip in kategoriler.items():
            for m in icerik.get(anahtar, []):
                # Veriyi topla
                durumlar = m.get('durumlar', {}).get('gelen', {})
                
                # Miktar belirleme (Toplama ise keşif eri, ticaret ise malzeme)
                if anahtar == 'toplama':
                    miktar = f"{durumlar.get('gonderilen_kesif_eri_sayisi', '?')} Keşif Eri"
                elif anahtar == 'saldiri':
                    miktar = m.get('hareket_ismi', 'Ordu')
                else:
                    miktar = f"{durumlar.get('malzeme_sayisi', 0)} {durumlar.get('malzeme_ismi', '')}"

                hareketler.append({
                    "tip": tip,
                    "gonderen": m.get('saldiran_oyuncu_ismi'),
                    "kullanici_adi": m.get('saldiran_kullanici_adi'),
                    "hedef": m.get('savunan_oyuncu_ismi'),
                    "miktar": miktar,
                    "baslangic": m.get('baslangic_tarihi'),
                    "varis": m.get('bitis_tarihi'),
                    "donuyormu": m.get('donuyormu', False)
                })

    # --- TARİHE GÖRE SIRALAMA (FİLTRELEME) ---
    def tarih_ayikla(item):
        try:
            # "19.3.2026 2:47:23.604" formatını parse ediyoruz
            return datetime.strptime(item['varis'], "%d.%m.%Y %H:%M:%S.%f")
        except:
            # Format değişirse veya hata olursa en sona atsın
            return datetime.max

    # Varış zamanı en yakın (en erken) olan en üstte olsun
    sirali_hareketler = sorted(hareketler, key=tarih_ayikla)

    return sirali_hareketler