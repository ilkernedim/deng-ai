from flask import Blueprint, current_app, jsonify, request

from . import database
from .services.ai_service import ai_service, AIServiceError
from .services.auth_service import auth_service

# arayuz yok, sadece json donduren uc noktalar var
sayfalar = Blueprint("sayfalar", __name__)
api = Blueprint("api", __name__, url_prefix="/api")


@sayfalar.route("/")
def index():
    return jsonify({"basari": True, "durum": "calisiyor"})


# render ve wix calisiyor mu diye kontrol icin
@sayfalar.route("/health")
def health():
    return jsonify({"basari": True, "durum": "calisiyor"})


# wixteki sohbet kutusu buraya mesaj gonderiyor
@api.route("/sohbet", methods=["POST"])
def sohbet():
    veri = request.get_json() or {}
    mesaj = veri.get("mesaj", "").strip()
    gecmis = veri.get("gecmis", [])

    # bos mesaj gelirse modele hic gitmiyor
    if mesaj == "":
        return jsonify({"basari": False, "hata": "Mesaj boş olamaz."}), 400

    try:
        cevap = ai_service.yanit_uret(mesaj, gecmis)
    except AIServiceError as hata:
        # render loglarinda sebebi gorunsun diye
        current_app.logger.error("[sohbet] yapay zeka servisi hatasi: %s", hata)
        return jsonify({"basari": False, "hata": "Danışman şu anda yanıt veremiyor, lütfen tekrar deneyin."}), 503

    return jsonify({"basari": True, "cevap": cevap})


# demo formu buraya geliyor, kayit olursa 201 doner
@api.route("/leads", methods=["POST"])
def lead_kaydet():
    veri = request.get_json() or {}

    isim = veri.get("isim", "").strip()
    telefon = veri.get("telefon", "").strip()
    sirket = veri.get("sirket", "").strip()
    ekip_buyuklugu = veri.get("ekip_buyuklugu", "").strip()
    eposta = veri.get("eposta", "").strip()
    mesaj = veri.get("mesaj", "").strip()

    if isim == "" or telefon == "" or sirket == "" or ekip_buyuklugu == "":
        return jsonify({"basari": False, "hata": "İsim, telefon, şirket ve ekip büyüklüğü alanları zorunludur."}), 400

    try:
        database.lead_ekle(isim, telefon, sirket, ekip_buyuklugu, eposta, mesaj)
    except Exception:
        current_app.logger.exception("[lead_kaydet] veritabanina yazilamadi")
        return jsonify({"basari": False, "hata": "Kayıt sırasında bir hata oluştu."}), 500

    return jsonify({"basari": True, "mesaj": "Talebiniz alındı, en kısa sürede sizinle iletişime geçeceğiz."}), 201


# yonetim girisi, dogruysa panelin kullanacagi anahtari doner
@api.route("/admin/giris", methods=["POST"])
def admin_giris():
    if not auth_service.aktif_mi():
        current_app.logger.error("[admin_giris] ADMIN_PASSWORD ayarlanmamis, giris kapali")
        return jsonify({"basari": False, "hata": "Yönetici girişi şu an kapalı."}), 503

    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    if auth_service.engelli_mi(ip):
        return jsonify({"basari": False, "hata": "Çok fazla hatalı deneme. Lütfen biraz sonra tekrar deneyin."}), 429

    veri = request.get_json(silent=True) or {}
    kullanici = str(veri.get("kullanici", "")).strip()
    sifre = str(veri.get("sifre", ""))

    if not auth_service.giris_dogru_mu(kullanici, sifre):
        auth_service.hata_kaydet(ip)
        return jsonify({"basari": False, "hata": "Kullanıcı adı veya şifre hatalı."}), 401

    auth_service.hata_temizle(ip)
    return jsonify({"basari": True, "anahtar": auth_service.anahtar_uret()})


# yonetim paneli talepleri buradan cekiyor, gecerli anahtar sart
@api.route("/leads", methods=["GET"])
def lead_listele():
    baslik = request.headers.get("Authorization", "")
    anahtar = baslik[7:] if baslik.startswith("Bearer ") else ""
    if not auth_service.anahtar_gecerli_mi(anahtar):
        return jsonify({"basari": False, "hata": "Yetkisiz erişim."}), 401

    try:
        leadler = database.tum_leadler()
    except Exception:
        current_app.logger.exception("[lead_listele] kayitlar okunamadi")
        return jsonify({"basari": False, "hata": "Kayıtlar okunamadı."}), 500

    return jsonify({"basari": True, "leadler": leadler})


# olmayan bir adrese gidilirse html yerine json hata donsun
@api.app_errorhandler(404)
def bulunamadi(hata):
    return jsonify({"basari": False, "hata": "Sayfa bulunamadı."}), 404
