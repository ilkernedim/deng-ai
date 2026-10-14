# database.py - Modul B: SQL SADECE bu dosyada bulunur
import sqlite3
from flask import current_app


def get_db():
    conn = sqlite3.connect(current_app.config["DATABASE_URL"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db(app):
    with app.app_context():
        conn = get_db()
        conn.execute(
            """CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                telefon TEXT NOT NULL,
                sirket TEXT NOT NULL,
                ekip_buyuklugu TEXT NOT NULL,
                eposta TEXT,
                mesaj TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.commit()
        conn.close()


def lead_ekle(isim, telefon, sirket, ekip_buyuklugu, eposta=None, mesaj=None):
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO leads (isim, telefon, sirket, ekip_buyuklugu, eposta, mesaj) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (isim, telefon, sirket, ekip_buyuklugu, eposta, mesaj),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def tum_leadler():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM leads ORDER BY tarih DESC, id DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
