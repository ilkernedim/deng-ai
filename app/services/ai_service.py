import requests
from flask import current_app

# anahtar yoksa uygulama cokmesin diye bu cevap donuyor
DEMO_CEVAP = "Su an demo modundayim. Bilgi almak icin demo talep formunu doldurabilirsiniz."


# groq tarafinda bir sorun olursa bu hatayi firlatiyoruz, routes bunu yakaliyor
class AIServiceError(Exception):
    pass


# yapay zeka ile konusan kisim sadece burada
class AIService:

    def _sistem_talimati(self):
        return current_app.config["BUSINESS_CONTEXT"]

    # groqa post istegi atar ve modelin yazdigi cevabi dondurur
    def _groq_cagir(self, mesajlar):
        adres = current_app.config["GROQ_URL"]
        anahtar = current_app.config["GROQ_API_KEY"]
        model = current_app.config["GROQ_MODEL"]

        basliklar = {"Authorization": "Bearer " + anahtar}
        govde = {
            "model": model,
            "messages": mesajlar,
            # dusuk tuttum ki cevaplar tutarli olsun
            "temperature": 0.4,
            # token harcamasini sinirlamak icin
            "max_tokens": 600,
        }

        try:
            cevap = requests.post(adres, headers=basliklar, json=govde, timeout=30)
            # 400 veya 500 gelirse direkt hataya duser
            cevap.raise_for_status()
            veri = cevap.json()
            return veri["choices"][0]["message"]["content"]
        except Exception as hata:
            raise AIServiceError(str(hata))

    # kullanicinin mesajini gecmisle birlikte modele gonderir
    def yanit_uret(self, mesaj, gecmis=None):
        if not current_app.config["GROQ_API_KEY"]:
            return DEMO_CEVAP

        mesajlar = [{"role": "system", "content": self._sistem_talimati()}]

        if gecmis:
            # son 10 mesaji aliyorum, hepsini gondermek token yer
            for eski in gecmis[-10:]:
                mesajlar.append({"role": eski["role"], "content": eski["content"]})

        mesajlar.append({"role": "user", "content": mesaj})

        return self._groq_cagir(mesajlar)


ai_service = AIService()
