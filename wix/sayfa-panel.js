(function () {
// Yonetim Paneli: leadleri Render RENDER_ADRESI'sinden ceker ve repeater'a basar
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

let tumLeadler = [];

$w.onReady(function () {
    $w("#rptLeads").onItemReady(function ($item, k) {
        $item("#txtAd").text = k.isim || "-";
        $item("#txtSirket").text = k.sirket || "-";
        $item("#txtEposta").text = k.eposta || "-";
        $item("#txtMesaj").text = k.mesaj || "-";
        $item("#txtTarih").text = k.tarih ? String(k.tarih).slice(0, 16) : "-";
    });

    $w("#btnYenile").onClick(function () { leadleriYukle(); });
    $w("#inpAra").onInput(function () { listeyiGoster(); });

    leadleriYukle();
});

async function leadleriYukle() {
    $w("#btnYenile").disable();
    const sonuc = await istekAt("panel", "/api/leads");
    if (sonuc.tamam) {
        tumLeadler = sonuc.veri.leadler || [];
    } else {
        tumLeadler = [];
        console.error("[panel] liste yuklenemedi, kaynak:", sonuc.kaynak, "kod:", sonuc.kod);
    }
    listeyiGoster();
    $w("#btnYenile").enable();
}

function listeyiGoster() {
    const aranan = ($w("#inpAra").value || "").toLowerCase().trim();
    const liste = tumLeadler.filter(function (k) {
        if (aranan === "") { return true; }
        return [k.isim, k.sirket, k.eposta].join(" ").toLowerCase().indexOf(aranan) !== -1;
    });

    const bugun = new Date().toISOString().slice(0, 10);
    const bugunSayisi = tumLeadler.filter(function (k) { return String(k.tarih || "").slice(0, 10) === bugun; }).length;
    $w("#txtToplamTalep").text = "Toplam talep: " + tumLeadler.length;
    $w("#txtBugun").text = "Bugün: " + bugunSayisi;

    $w("#rptLeads").data = liste.map(function (k, i) {
        return Object.assign({}, k, { _id: String(k.id !== undefined ? k.id : i) });
    });
}
})();
