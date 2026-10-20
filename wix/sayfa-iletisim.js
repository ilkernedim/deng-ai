(function () {
// Iletisim: demo talebini Render RENDER_ADRESI'sine gonderir, kayit yonetim paneline duser
const RENDER_ADRESI = "https://deng-ai.onrender.com";
// Render'a istek atar. Hatanin nerede oldugunu konsola yazar:
// AG (Render'a ulasilamadi), JSON (cevap bozuk) veya SUNUCU (HTTP kodu 4xx/5xx)
async function istekAt(etiket, yol, secenek) {
    let yanit;
    try {
        yanit = await fetch(RENDER_ADRESI + yol, secenek);
    } catch (hata) {
        console.error("[" + etiket + "] AG HATASI: Render'a ulasilamadi (uyuyor veya adres yanlis olabilir)", hata);
        return { tamam: false, kod: 0, veri: null, kaynak: "ag" };
    }
    let veri = null;
    try {
        veri = await yanit.json();
    } catch (hata) {
        console.error("[" + etiket + "] JSON HATASI: cevap okunamadi, HTTP " + yanit.status, hata);
        return { tamam: false, kod: yanit.status, veri: null, kaynak: "json" };
    }
    if (!yanit.ok || !veri.basari) {
        console.error("[" + etiket + "] SUNUCU HATASI: HTTP " + yanit.status + " | " + (veri && veri.hata));
        return { tamam: false, kod: yanit.status, veri: veri, kaynak: "sunucu" };
    }
    return { tamam: true, kod: yanit.status, veri: veri, kaynak: "" };
}


$w.onReady(function () {
    $w("#btnDemo").onClick(demoGonder);
});

function durumYaz(mesaj, hata) {
    $w("#txtDurum").text = mesaj;
    $w("#txtDurum").style.color = hata ? "#B91C1C" : "#0F766E";
}

async function demoGonder() {
    const ad = ($w("#inpAd").value || "").trim();
    const telefon = ($w("#inpTelefon").value || "").trim();
    const sirket = ($w("#inpSirket").value || "").trim();
    const ekip = ($w("#inpEkipBuyuklugu").value || "").trim();
    const eposta = ($w("#inpEposta").value || "").trim();
    const not = ($w("#inpNot").value || "").trim();

    if (ad === "" || telefon === "" || sirket === "" || ekip === "") {
        durumYaz("Lütfen ad soyad, telefon, şirket ve ekip büyüklüğü alanlarını doldurun.", true);
        return;
    }

    $w("#btnDemo").disable();
    durumYaz("Gönderiliyor...", false);

    const sonuc = await istekAt("demo-formu", "/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isim: ad, telefon: telefon, sirket: sirket, ekip_buyuklugu: ekip, eposta: eposta, mesaj: not })
    });

    if (sonuc.tamam && sonuc.kod === 201) {
        durumYaz(sonuc.veri.mesaj || "Talebiniz alındı.", false);
        ["#inpAd", "#inpTelefon", "#inpSirket", "#inpEkipBuyuklugu", "#inpEposta", "#inpNot"].forEach(function (id) { $w(id).value = ""; });
    } else if (sonuc.kaynak === "sunucu") {
        durumYaz((sonuc.veri && sonuc.veri.hata) || "Talep gönderilemedi, lütfen tekrar deneyin.", true);
    } else {
        durumYaz("Bağlantı kurulamadı, lütfen biraz sonra tekrar deneyin.", true);
    }
    $w("#btnDemo").enable();
}
})();
(function () {
// DENG-AI sohbet balonu
$w.onReady(function () {
    chatBaslat();
});

// ---- DENG-AI sohbet balonu: yanitlar Render'daki /api/sohbet adresinden gelir ----
const RENDER_ADRESI = "https://deng-ai.onrender.com";
// Render'a istek atar. Hatanin nerede oldugunu konsola yazar:
// AG (Render'a ulasilamadi), JSON (cevap bozuk) veya SUNUCU (HTTP kodu 4xx/5xx)
async function istekAt(etiket, yol, secenek) {
    let yanit;
    try {
        yanit = await fetch(RENDER_ADRESI + yol, secenek);
    } catch (hata) {
        console.error("[" + etiket + "] AG HATASI: Render'a ulasilamadi (uyuyor veya adres yanlis olabilir)", hata);
        return { tamam: false, kod: 0, veri: null, kaynak: "ag" };
    }
    let veri = null;
    try {
        veri = await yanit.json();
    } catch (hata) {
        console.error("[" + etiket + "] JSON HATASI: cevap okunamadi, HTTP " + yanit.status, hata);
        return { tamam: false, kod: yanit.status, veri: null, kaynak: "json" };
    }
    if (!yanit.ok || !veri.basari) {
        console.error("[" + etiket + "] SUNUCU HATASI: HTTP " + yanit.status + " | " + (veri && veri.hata));
        return { tamam: false, kod: yanit.status, veri: veri, kaynak: "sunucu" };
    }
    return { tamam: true, kod: yanit.status, veri: veri, kaynak: "" };
}

let sohbetGecmisi = [];
let sohbetMesgul = false;

let kutuAcik = false;
let sonTik = 0;

function chatBaslat() {
    try {
        $w("#btnChat").onClick(function () {
            const simdi = Date.now();
            if (simdi - sonTik < 500) { return; }
            sonTik = simdi;
            kutuAcik = !kutuAcik;
            if (kutuAcik) {
                $w("#boxChat").show("fade", { duration: 250 });
            } else {
                $w("#boxChat").hide("fade", { duration: 200 });
            }
        });

        $w("#btnGonder").onClick(function () { mesajGonder(); });
        $w("#inpMesaj").onKeyPress(function (olay) {
            if (olay.key === "Enter") { mesajGonder(); }
        });
        $w("#boxChat").hide();
        console.log("[sohbet] hazir, kutu gizlendi");
    } catch (hata) {
        console.error("[sohbet] BASLATMA HATASI (kimlik yanlis veya oge yok olabilir):", hata);
    }
}

function sohbeteYaz(kim, metin) {
    const onceki = $w("#txtMesajlar").text || "";
    const satirlar = (onceki + "\n\n" + kim + ": " + metin).split("\n\n");
    $w("#txtMesajlar").text = satirlar.slice(-2).join("\n\n");
}

async function mesajGonder() {
    const mesaj = ($w("#inpMesaj").value || "").trim();
    if (mesaj === "" || sohbetMesgul) { return; }

    sohbetMesgul = true;
    $w("#inpMesaj").value = "";
    sohbeteYaz("Siz", mesaj);
    sohbeteYaz("DENG-AI", "Yazıyor...");

    const sonuc = await istekAt("sohbet", "/api/sohbet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mesaj: mesaj, gecmis: sohbetGecmisi.slice(-10) })
    });

    if (sonuc.tamam) {
        sohbetGecmisi.push({ role: "user", content: mesaj });
        sohbetGecmisi.push({ role: "assistant", content: sonuc.veri.cevap });
        degistirSon(sonuc.veri.cevap);
    } else if (sonuc.kaynak === "sunucu") {
        degistirSon((sonuc.veri && sonuc.veri.hata) || "Şu anda yanıt veremiyorum.");
    } else {
        degistirSon("Bağlantı kurulamadı, lütfen tekrar deneyin.");
    }
    sohbetMesgul = false;
}

function degistirSon(cevap) {
    const parcalar = ($w("#txtMesajlar").text || "").split("\n\n");
    parcalar[parcalar.length - 1] = "DENG-AI: " + cevap;
    $w("#txtMesajlar").text = parcalar.join("\n\n");
}
})();
