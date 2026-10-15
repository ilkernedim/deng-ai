import sqlite3
from flask import current_app


# veritabanina baglanir, satirlar sozluk gibi okunabilsin diye row_factory var
def get_db():
    baglanti = sqlite3.connect(current_app.config["DATABASE_URL"])
    baglanti.row_factory = sqlite3.Row
    return baglanti


# uygulama acilirken leads tablosu yoksa olusturur
def init_db(app):
    with app.app_context():
        baglanti = get_db()
        baglanti.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                telefon TEXT NOT NULL,
                sirket TEXT NOT NULL,
                ekip_buyuklugu TEXT NOT NULL,
                eposta TEXT,
                mesaj TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        baglanti.commit()
        baglanti.close()


# demo formundan gelen talebi kaydeder
# soru isaretleri sayesinde veri sorguya direkt yazilmiyor, sql injection olmuyor
def lead_ekle(isim, telefon, sirket, ekip_buyuklugu, eposta, mesaj):
    baglanti = get_db()
    baglanti.execute(
        "INSERT INTO leads (isim, telefon, sirket, ekip_buyuklugu, eposta, mesaj) VALUES (?, ?, ?, ?, ?, ?)",
        (isim, telefon, sirket, ekip_buyuklugu, eposta, mesaj)
    )
    baglanti.commit()
    baglanti.close()


# panel icin butun talepleri yeniden eskiye dogru getirir
def tum_leadler():
    baglanti = get_db()
    satirlar = baglanti.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    baglanti.close()

    leadler = []
    for satir in satirlar:
        leadler.append(dict(satir))
    return leadler
