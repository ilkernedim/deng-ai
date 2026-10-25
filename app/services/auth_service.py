import hmac
import time

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash

# ayni ip arka arkaya yanlis girerse bir sure bekletilir
DENEME_SAYISI = 5
BEKLEME_SANIYE = 600


# giris ve anahtar islemleri sadece burada
class AuthService:

    def __init__(self):
        # ip adresine gore hatali giris zamanlari (bellekte tutuluyor)
        self._hatalar = {}

    def _imzalayici(self):
        # sifre bilgisini de anahtara kattim, sifre degisince eski anahtarlar gecersiz olur
        gizli = current_app.config["SECRET_KEY"] + self._sifre_kaynagi()
        return URLSafeTimedSerializer(gizli, salt="admin-giris")

    # hangi sifre bilgisinin gecerli oldugunu secer: ortamdaki hash, ortamdaki duz sifre, demo hashi
    def _sifre_kaynagi(self):
        ayar = current_app.config
        return ayar["ADMIN_PASSWORD_HASH"] or ayar["ADMIN_PASSWORD"] or ayar["ADMIN_VARSAYILAN_HASH"]

    # sifreyi hashle karsilastirir, duz yazi ayar varsa sabit sureli karsilastirma yapar
    def _sifre_dogru_mu(self, sifre):
        ayar = current_app.config
        if ayar["ADMIN_PASSWORD_HASH"]:
            return self._hash_kontrol(ayar["ADMIN_PASSWORD_HASH"], sifre)
        if ayar["ADMIN_PASSWORD"]:
            return hmac.compare_digest(sifre.encode(), ayar["ADMIN_PASSWORD"].encode())
        return self._hash_kontrol(ayar["ADMIN_VARSAYILAN_HASH"], sifre)

    # bozuk bir hash ayari uygulamayi cokertmesin, giris reddedilir ve loga yazilir
    def _hash_kontrol(self, hash_degeri, sifre):
        try:
            return check_password_hash(hash_degeri, sifre)
        except ValueError:
            current_app.logger.error("[auth] ADMIN_PASSWORD_HASH gecersiz bicimde, giris reddedildi")
            return False

    # varsayilan hash oldugu icin giris her zaman acik, bos sifre ayari kapatmaz
    def aktif_mi(self):
        return bool(self._sifre_kaynagi())

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

    # kullanici adi ve sifre ikisi de hesaplanir, hangisinin yanlis oldugu sureden anlasilmasin
    def giris_dogru_mu(self, kullanici, sifre):
        kullanici_ok = hmac.compare_digest(kullanici.encode(), current_app.config["ADMIN_USER"].encode())
        sifre_ok = self._sifre_dogru_mu(sifre)
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
