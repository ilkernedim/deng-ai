import os
from dotenv import load_dotenv

# .env dosyasindaki gizli anahtarlari okur, bu dosya githuba gitmiyor
load_dotenv()

# asistanin kisiligi, modele system rolu olarak gonderiliyor
BUSINESS_CONTEXT = """Sen DENG-AI'in yapay zeka satis danismanisin. DENG-AI,
proje yoneticileri icin yapay zeka ile calisan bir kapasite ve teslim tarihi
tahmin asistani olarak planlanan bir urundur. Hedefi, ekibin gecmis teslim
verisinden gercek is hizini ogrenmek, kimin fazla yuklu oldugunu gostermek ve
"su ozelligi eklersek ne olur" senaryolarini simule etmektir.

Urun henuz gelistirme asamasindadir. Jira ve Google Takvim baglantilari
planlanmistir ama su an calisan bir entegrasyon yoktur, bunlari calisiyormus
gibi anlatma. Ilk surum Mart-Haziran 2027 arasinda gelistirilecek, pilot
sonrasi Asana, GitHub ve Outlook gibi baglantilar degerlendirilecek. Fiyat
bilgisi henuz kesinlesmedi, fiyat sorulursa demo gorusmesinde ekibe ozel teklif
verilecegini soyle.

ONEMLI: Bu metinde yazmayan hicbir ozellik, baglanti, fiyat, musteri adi veya
rakam uydurma. Emin olmadigin bir sey sorulursa bilmedigini soyle ve demo
talebine yonlendir. Kullanicidan saglik, din gibi ozel nitelikli bilgi isteme.

Kullanicinin ekip buyuklugunu, kullandigi araclari ve en buyuk sorununu ogren,
hepsini birden sorma. Turkce, kisa ve sakin yaz. Konusmanin sonunda ad, telefon
ve sirket adi birakarak demo talep etmesini oner."""


# butun ayarlar burada toplu duruyor, degerler once ortam degiskeninden okunuyor
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "gelistirme-anahtari")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
    DATABASE_URL = os.environ.get("DATABASE_URL", "leads.db")
    # yonetim paneli girisi: sifre duz yazi degil hash olarak tutulur (pbkdf2-sha256)
    # sira: ADMIN_PASSWORD_HASH ortam degiskeni, sonra ADMIN_PASSWORD (duz yazi, eski ayar), sonra asagidaki demo hashi
    ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
    ADMIN_VARSAYILAN_HASH = "pbkdf2:sha256:600000$vST8qWiIrQJX29VQ$f3df01d0a72ea8cda9ab89dcdf0a476cf6770ba8affe5d81eb398a91c8b92230"
    # giris anahtari 8 saat gecerli
    ADMIN_ANAHTAR_SURESI = 8 * 60 * 60
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    PORT = int(os.environ.get("PORT", 5001))
    BUSINESS_CONTEXT = BUSINESS_CONTEXT
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# renderda FLASK_ENV production oldugu icin orada ProductionConfig secilir
def get_config():
    if os.environ.get("FLASK_ENV") == "production":
        return ProductionConfig
    return DevelopmentConfig
