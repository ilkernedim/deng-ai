import requests
from flask import current_app

DEMO_CEVAP = "Su an demo modundayim. Bilgi almak icin demo talep formunu doldurabilirsiniz."


class AIServiceError(Exception):
    pass


class AIService:

    def _sistem_talimati(self):
        return current_app.config["BUSINESS_CONTEXT"]

    def _groq_cagir(self, mesajlar):
        adres = current_app.config["GROQ_URL"]
        anahtar = current_app.config["GROQ_API_KEY"]
        model = current_app.config["GROQ_MODEL"]

        basliklar = {"Authorization": "Bearer " + anahtar}
        govde = {
            "model": model,
            "messages": mesajlar,
            "temperature": 0.4,
            "max_tokens": 600,
        }

        try:
            cevap = requests.post(adres, headers=basliklar, json=govde, timeout=30)
            cevap.raise_for_status()
            veri = cevap.json()
            return veri["choices"][0]["message"]["content"]
        except Exception as hata:
            raise AIServiceError(str(hata))

    def yanit_uret(self, mesaj, gecmis=None):
        if not current_app.config["GROQ_API_KEY"]:
            return DEMO_CEVAP

        mesajlar = [{"role": "system", "content": self._sistem_talimati()}]

        if gecmis:
            for eski in gecmis[-10:]:
                mesajlar.append({"role": eski["role"], "content": eski["content"]})

        mesajlar.append({"role": "user", "content": mesaj})

        return self._groq_cagir(mesajlar)


ai_service = AIService()
