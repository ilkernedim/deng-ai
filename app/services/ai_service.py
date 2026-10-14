# ai_service.py - Modul C: yapay zeka cagrisi SADECE bu dosyada bulunur
import requests
from flask import current_app

DEMO_CEVAP = ("Su an demo modundayim, yapay zeka baglantisi kurulmadi. "
              "DENG-AI hakkinda bilgi almak icin demo talep formunu doldurabilirsiniz.")


class AIServiceError(Exception):
    pass


class AIService:
    def _sistem_talimati(self):
        return current_app.config["BUSINESS_CONTEXT"]

    def _groq_cagir(self, mesajlar):
        cfg = current_app.config
        try:
            r = requests.post(
                cfg["GROQ_URL"],
                headers={"Authorization": f"Bearer {cfg['GROQ_API_KEY']}"},
                json={"model": cfg["GROQ_MODEL"], "messages": mesajlar,
                      "temperature": 0.4, "max_tokens": 600},
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, ValueError) as e:
            raise AIServiceError(str(e)) from e

    def yanit_uret(self, mesaj, gecmis=None):
        if not current_app.config["GROQ_API_KEY"]:
            return DEMO_CEVAP
        mesajlar = [{"role": "system", "content": self._sistem_talimati()}]
        for m in (gecmis or [])[-10:]:
            if m.get("role") in ("user", "assistant") and m.get("content"):
                mesajlar.append({"role": m["role"], "content": str(m["content"])})
        mesajlar.append({"role": "user", "content": mesaj})
        return self._groq_cagir(mesajlar)


ai_service = AIService()
