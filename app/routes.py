from flask import Blueprint, jsonify, render_template, request

from . import database
from .services.ai_service import ai_service, AIServiceError

# sayfalar html donduruyor, api ise json donduruyor
sayfalar = Blueprint("sayfalar", __name__)
api = Blueprint("api", __name__, url_prefix="/api")


@sayfalar.route("/")
def index():
    return render_template("index.html")


@sayfalar.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


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
    except AIServiceError:
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
        return jsonify({"basari": False, "hata": "Kayıt sırasında bir hata oluştu."}), 500

    return jsonify({"basari": True, "mesaj": "Talebiniz alındı, en kısa sürede sizinle iletişime geçeceğiz."}), 201


# yonetim paneli talepleri buradan cekiyor
@api.route("/leads", methods=["GET"])
def lead_listele():
    try:
        leadler = database.tum_leadler()
    except Exception:
        return jsonify({"basari": False, "hata": "Kayıtlar okunamadı."}), 500

    return jsonify({"basari": True, "leadler": leadler})


# olmayan bir adrese gidilirse html yerine json hata donsun
@api.app_errorhandler(404)
def bulunamadi(hata):
    return jsonify({"basari": False, "hata": "Sayfa bulunamadı."}), 404
