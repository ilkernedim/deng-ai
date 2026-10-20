import wixLocationFrontend from "wix-location-frontend";

// ---- DENG-AI sohbet balonu: yanitlar Render'daki /api/sohbet adresinden gelir ----
const CHAT_API = "https://deng-ai.onrender.com";
let sohbetGecmisi = [];
let sohbetMesgul = false;

$w.onReady(function () {
    const yol = (wixLocationFrontend.path || []).join("/").toLowerCase();
    if (yol.indexOf("kvkk") !== -1 || yol.indexOf("yonetim") !== -1) {
        $w("#btnChat").hide();
        $w("#boxChat").hide();
        return;
    }
    $w("#boxChat").hide();

    $w("#btnChat").onClick(function () {
        if ($w("#boxChat").hidden) {
            $w("#boxChat").show("fade", { duration: 250 }).then(sohbetiBagla);
        } else {
            $w("#boxChat").hide("fade", { duration: 200 });
        }
    });

});

let baglandi = false;
function sohbetiBagla() {
    if (baglandi) { return; }
    baglandi = true;
    console.log("bagla basladi");
    try {
        console.log("btnGonder id:", $w("#btnGonder").id, "tip:", $w("#btnGonder").type);
        $w("#btnGonder").onClick(function () {
            console.log("gonder tiklandi");
            mesajGonder();
        });
    } catch (hata) {
        console.log("bagla hatasi:", String(hata));
    }
}

function sohbeteYaz(kim, metin) {
    const onceki = $w("#txtMesajlar").text || "";
    const satirlar = (onceki + "\n\n" + kim + ": " + metin).split("\n\n");
    $w("#txtMesajlar").text = satirlar.slice(-8).join("\n\n");
}

async function mesajGonder() {
    const mesaj = ($w("#inpMesaj").value || "").trim();
    if (mesaj === "" || sohbetMesgul) { return; }

    sohbetMesgul = true;
    $w("#inpMesaj").value = "";
    sohbeteYaz("Siz", mesaj);
    sohbeteYaz("DENG-AI", "Yazıyor...");

    try {
        const yanit = await fetch(CHAT_API + "/api/sohbet", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mesaj: mesaj, gecmis: sohbetGecmisi.slice(-10) })
        });
        const veri = await yanit.json();
        const cevap = veri.basari ? veri.cevap : (veri.hata || "Şu anda yanıt veremiyorum.");

        sohbetGecmisi.push({ role: "user", content: mesaj });
        if (veri.basari) { sohbetGecmisi.push({ role: "assistant", content: cevap }); }
        degistirSon(cevap);
    } catch (hata) {
        console.error("Sohbet hatasi:", hata);
        degistirSon("Bağlantı kurulamadı, lütfen tekrar deneyin.");
    }
    sohbetMesgul = false;
}

function degistirSon(cevap) {
    const parcalar = ($w("#txtMesajlar").text || "").split("\n\n");
    parcalar[parcalar.length - 1] = "DENG-AI: " + cevap;
    $w("#txtMesajlar").text = parcalar.join("\n\n");
}
