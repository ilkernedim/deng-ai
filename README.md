# DENG-AI Akıllı Satış Asistanı

## Mimari

| Dosya | Sorumluluk |
|---|---|
| `run.py` | Giriş noktası |
| `config.py` | Ayarlar ve sistem talimatı (BUSINESS_CONTEXT) |
| `app/__init__.py` | Uygulama fabrikası (create_app) |
| `app/database.py` | Veritabanı işlemleri, SQL sadece burada |
| `app/services/ai_service.py` | Groq API çağrısı, yapay zeka sadece burada |
| `app/routes.py` | HTTP rotaları, sadece yönlendirme |
| `app/templates/` | Karşılama sayfası ve yönetim paneli |

## Uç noktalar

| Yol | Görev |
|---|---|
| `GET /` | Karşılama sayfası |
| `GET /dashboard` | Yönetim paneli |
| `GET /health` | Canlılık kontrolü |
| `POST /api/sohbet` | Yapay zeka danışmanı |
| `POST /api/leads` | Demo talebi kaydı |
| `GET /api/leads` | Talepleri listeleme |
