import hmac
import time

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

# ayni ip arka arkaya yanlis girerse bir sure bekletilir
DENEME_SAYISI = 5
BEKLEME_SANIYE = 600


# giris ve anahtar islemleri sadece burada
class AuthService:

    def __init__(self):
        # ip adresine gore hatali giris zamanlari (bellekte tutuluyor)
        self._hatalar = {}

    def _imzalayici(self):
        # sifreyi de anahtara kattim, SECRET_KEY varsayilan kalsa bile anahtar sahte uretilemez
        gizli = current_app.config["SECRET_KEY"] + current_app.config["ADMIN_PASSWORD"]
        return URLSafeTimedSerializer(gizli, salt="admin-giris")

    # sifre ayarlanmadiysa giris tamamen kapali kalir
    def aktif_mi(self):
        return bool(current_app.config["ADMIN_PASSWORD"])

    # ip cok fazla yanlis denediyse True doner
    def engelli_mi(self, ip):
        simdi = time.time()
        zamanlar = [z for z in self._hatalar.get(ip, []) if simdi - z < BEKLEME_SANIYE]
        self._hatalar[ip] = zamanlar
        return len(zamanlar) >= DENEME_SAYISI

    def hata_kaydet(self, ip):
        self._hatalar.setdefault(ip, []).append(time.time())

    def hata_temizle(self, ip):
        self._hatalar.pop(ip, None)

    # compare_digest ile karsilastiriyorum ki sure farkindan sifre tahmin edilemesin
    def giris_dogru_mu(self, kullanici, sifre):
        kullanici_ok = hmac.compare_digest(kullanici.encode(), current_app.config["ADMIN_USER"].encode())
        sifre_ok = hmac.compare_digest(sifre.encode(), current_app.config["ADMIN_PASSWORD"].encode())
        return kullanici_ok and sifre_ok

    # giris basariliysa panelin kullanacagi imzali anahtar uretir
    def anahtar_uret(self):
        return self._imzalayici().dumps({"rol": "admin"})

    # anahtar gecerli ve suresi dolmamissa True
    def anahtar_gecerli_mi(self, anahtar):
        if not anahtar or not self.aktif_mi():
            return False
        try:
            veri = self._imzalayici().loads(anahtar, max_age=current_app.config["ADMIN_ANAHTAR_SURESI"])
        except (BadSignature, SignatureExpired):
            return False
        return veri.get("rol") == "admin"


auth_service = AuthService()
