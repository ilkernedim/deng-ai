# routes.py - Modul D: sadece yonlendirir, SQL veya AI kodu icermez
import logging
from flask import Blueprint, jsonify, render_template, request

from . import database
from .services.ai_service import ai_service, AIServiceError

log = logging.getLogger(__name__)
sayfalar = Blueprint("sayfalar", __name__)
api = Blueprint("api", __name__, url_prefix="/api")

ZORUNLU = ("isim", "telefon", "sirket", "ekip_buyuklugu")


@sayfalar.route("/")
def index():
    return render_template("index.html")


@sayfalar.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@sayfalar.route("/health")
def health():
    return jsonify({"basari": True, "durum": "calisiyor"})


@api.route("/sohbet", methods=["POST"])
def sohbet():
    veri = request.get_json(silent=True) or {}
    mesaj = str(veri.get("mesaj", "")).strip()
    if not mesaj:
        return jsonify({"basari": False, "hata": "Mesaj boş olamaz."}), 400
    try:
        cevap = ai_service.yanit_uret(mesaj, veri.get("gecmis"))
    except AIServiceError:
        log.exception("AI servisi hatasi")
        return jsonify({"basari": False,
                        "hata": "Danışman şu anda yanıt veremiyor, lütfen tekrar deneyin."}), 503
    return jsonify({"basari": True, "cevap": cevap})


@api.route("/leads", methods=["POST"])
def lead_kaydet():
    veri = request.get_json(silent=True) or {}
    alanlar = {k: str(veri.get(k, "")).strip() for k in ZORUNLU + ("eposta", "mesaj")}
    if not all(alanlar[k] for k in ZORUNLU):
        return jsonify({"basari": False,
                        "hata": "İsim, telefon, şirket ve ekip büyüklüğü alanları zorunludur."}), 400
    try:
        database.lead_ekle(alanlar["isim"], alanlar["telefon"], alanlar["sirket"],
                           alanlar["ekip_buyuklugu"], alanlar["eposta"] or None,
                           alanlar["mesaj"] or None)
    except Exception:
        log.exception("Veritabani hatasi")
        return jsonify({"basari": False, "hata": "Kayıt sırasında bir hata oluştu."}), 500
    return jsonify({"basari": True,
                    "mesaj": "Talebiniz alındı, en kısa sürede sizinle iletişime geçeceğiz."}), 201


@api.route("/leads", methods=["GET"])
def lead_listele():
    try:
        return jsonify({"basari": True, "leadler": database.tum_leadler()})
    except Exception:
        log.exception("Veritabani hatasi")
        return jsonify({"basari": False, "hata": "Kayıtlar okunamadı."}), 500


@api.app_errorhandler(404)
def bulunamadi(_):
    return jsonify({"basari": False, "hata": "Sayfa bulunamadı."}), 404
