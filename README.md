# DENG-AI Akıllı Satış Asistanı

DENG-AI'ın satış danışmanı. Sohbet eden yapay zeka, demo talebi (lead) toplayan form
ve talepleri gösteren yönetici paneli için JSON döndüren Flask arka ucu. Arayüz Wix
Studio sitesinde, bu depo yalnızca arka uçtur.

## Mimari

| Dosya | Sorumluluk |
|---|---|
| `run.py` | Giriş noktası |
| `config.py` | Ayarlar ve sistem talimatı (BUSINESS_CONTEXT) |
| `app/__init__.py` | Uygulama fabrikası (create_app) |
| `app/database.py` | Veritabanı işlemleri (SQLite), SQL sadece burada |
| `app/services/ai_service.py` | Groq API çağrısı, yapay zeka sadece burada |
| `app/services/auth_service.py` | Yönetici girişi ve imzalı anahtar işlemleri |
| `app/routes.py` | HTTP rotaları, sadece yönlendirme |

## Uç noktalar

| Yol | Görev | Yetki |
|---|---|---|
| `GET /` | Canlılık cevabı (JSON) | Herkes |
| `GET /health` | Canlılık kontrolü | Herkes |
| `POST /api/sohbet` | Yapay zeka danışmanı | Herkes |
| `POST /api/leads` | Demo talebi kaydı | Herkes |
| `POST /api/admin/giris` | Kullanıcı adı ve şifre ile giriş, anahtar döner | Herkes |
| `GET /api/leads` | Talepleri listeleme | Yönetici anahtarı |

## Yönetici girişi

`POST /api/admin/giris` gövdesi `{"kullanici": "...", "sifre": "..."}`. Doğruysa 8 saat
geçerli imzalı bir anahtar döner. Panel bu anahtarı `Authorization: Bearer <anahtar>`
başlığıyla `GET /api/leads` isteğine ekler. Anahtarsız veya süresi dolmuş istek 401 alır.
Aynı IP 5 kez yanlış girerse 10 dakika boyunca 429 alır.

Şifre koda düz yazı olarak girmez, hash (pbkdf2-sha256) olarak saklanır. Ayarlar ortam
değişkenlerinden okunur: `ADMIN_USER` (varsayılan `admin`), `ADMIN_PASSWORD_HASH` (öncelikli)
ve `ADMIN_PASSWORD` (düz yazı, Render'daki eski ayar için). İkisi de tanımlı değilse
`config.py` içindeki demo hash'i geçerlidir. Yeni şifre için hash üretmek:

```bash
./venv/bin/python -c "from werkzeug.security import generate_password_hash as g; print(g('yeni-sifre', method='pbkdf2:sha256:600000'))"
```

Çıkan değer Render'da `ADMIN_PASSWORD_HASH` olarak tanımlanır. Şifre değişince eski anahtarlar
geçersiz olur.

## Çalıştırma

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env        # GROQ_API_KEY ve SECRET_KEY değerlerini doldur
./venv/bin/python run.py    # http://localhost:5001
```

Canlıda `gunicorn run:app` ile çalışır (Render). Render'da SQLite dosyası geçicidir,
yeniden dağıtımda veya uykudan sonra kayıtlar silinebilir.
