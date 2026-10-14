# config.py - Modul A: tum ayarlarin tek kaynagi
import os
from dotenv import load_dotenv

load_dotenv()

BUSINESS_CONTEXT = """Sen DENG-AI'in yapay zeka satis danismanisin. DENG-AI,
proje yoneticileri icin yapay zeka ile calisan bir kapasite ve teslim tarihi
tahmin asistanidir. Ekibin gecmis Jira ve takvim verisinden gercek is hizini
ogrenir, kimin fazla yuklu oldugunu gosterir ve "su ozelligi eklersek ne olur"
senaryolarini simule eder.

Su an desteklenen baglantilar: Jira ve Google Takvim. Asana, GitHub ve Outlook
ileride eklenecek. Fiyat bilgisi henuz kesinlesmedi, fiyat sorulursa demo
gorusmesinde ekibe ozel teklif verilecegini soyle.

ONEMLI: Bu metinde yazmayan hicbir ozellik, baglanti, fiyat, musteri adi veya
rakam uydurma. Emin olmadigin bir sey sorulursa bilmedigini soyle ve demo
talebine yonlendir. Kullanicidan saglik, din gibi ozel nitelikli bilgi isteme.

Kullanicinin ekip buyuklugunu, kullandigi araclari ve en buyuk sorununu ogren,
hepsini birden sorma. Turkce, kisa ve sakin yaz. Konusmanin sonunda ad, telefon
ve sirket adi birakarak demo talep etmesini oner."""


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "gelistirme-anahtari")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
    DATABASE_URL = os.environ.get("DATABASE_URL", "leads.db")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    PORT = int(os.environ.get("PORT", 5001))  # 5000'i macOS AirPlay isgal ediyor
    BUSINESS_CONTEXT = BUSINESS_CONTEXT
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


def get_config():
    if os.environ.get("FLASK_ENV") == "production":
        return ProductionConfig
    return DevelopmentConfig
