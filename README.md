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

Ayarlar ortam değişkenlerinden okunur: `ADMIN_USER` (varsayılan `admin`) ve
`ADMIN_PASSWORD` (`config.py` içinde demo için varsayılan değeri var, Render'da
ortam değişkeni olarak tanımlanırsa o geçerli olur).

## Çalıştırma

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env        # GROQ_API_KEY ve SECRET_KEY değerlerini doldur
./venv/bin/python run.py    # http://localhost:5001
```

Canlıda `gunicorn run:app` ile çalışır (Render). Render'da SQLite dosyası geçicidir,
yeniden dağıtımda veya uykudan sonra kayıtlar silinebilir.
