"""Tablo 1 — Toprak besin referans aralıkları bileşeni."""

from __future__ import annotations

import streamlit as st

from tarla_ai.soil.reference import SOIL_REFERENCE
from tarla_ai.ui.html import cap, fmt, th, tip

PARAM_TIPS: dict[str, str] = {
    "pH": (
        "Toprağın asit mi yoksa bazik mi olduğunu gösteren 0–14 arası bir sayı. "
        "7 nötrdür. 7'den küçükse asit, büyükse bazik (alkali). "
        "Buğday ve arpa 6.5–7.8 arasını sever. "
        "Bu aralığın dışında gübreler işe yaramaz çünkü besin maddeleri bitkiye ulaşamaz."
    ),
    "Organik Madde": (
        "Topraktaki çürümüş bitki ve hayvan kalıntılarının yüzdesi. "
        "Toprak ne kadar 'canlı' olduğunun göstergesi. "
        "Yüksek organik madde suyu tutar, gübre kaybını azaltır, toprağı gevşetir. "
        "İç Anadolu toprakları genelde %1–2 ile düşük seviyededir."
    ),
    "Toplam Azot": (
        "Topraktaki azot elementinin toplam yüzdesi. "
        "Azot (N), bitkinin en çok ihtiyaç duyduğu besin maddesidir — yaprak, sap ve tane gelişimi için şarttır. "
        "Eksikliğinde yapraklar sararır, bitki bodur kalır."
    ),
    "Alınabilir Fosfor (P₂O₅)": (
        "Bitkinin kökten alabileceği fosfor miktarı. "
        "Fosfor (P) kök gelişimi, çiçeklenme ve tane bağlama için kritiktir. "
        "P₂O₅ fosforun laboratuvarda ölçülen oksit formudur. "
        "Kireçli toprağa yüzeyden verilen fosfor hareketsiz kalır — ekimle birlikte toprağa karıştırılmalıdır."
    ),
    "Alınabilir Potasyum (K₂O)": (
        "Bitkinin kökten alabileceği potasyum miktarı. "
        "Potasyum (K) bitkinin su dengesini korur, hastalıklara direncini artırır ve tane ağırlığını etkiler. "
        "K₂O potasyumun laboratuvarda ölçülen oksit formudur. "
        "İç Anadolu killi topraklarında genellikle yeterli düzeyde bulunur."
    ),
    "Kalsiyum (Ca)": (
        "Hücre duvarı yapısı için gerekli temel besin. "
        "Kireçli İç Anadolu topraklarında kalsiyum zaten bol bulunur, eksikliği görülmez. "
        "Çok fazla kalsiyum ise magnezyum ve potasyumun bitkiye geçişini zorlaştırabilir."
    ),
    "Magnezyum (Mg)": (
        "Klorofil molekülünün merkezinde yer alan element. "
        "Klorofil olmadan fotosentez (güneş ışığından besin üretimi) yapılamaz. "
        "Eksikliğinde yapraklar sararmaya başlar, damarlar yeşil kalır."
    ),
    "EC / Tuzluluk": (
        "Toprağın elektrik iletkenliği — topraktaki çözünmüş tuz miktarını gösterir. "
        "dS/m birimi kullanılır. Tuz fazla olunca bitki kökten su alamaz, 'susuz' kalır. "
        "Kıraç İç Anadolu topraklarında genelde düşük ve sorun değildir."
    ),
    "Kireç (CaCO₃)": (
        "Topraktaki kalsiyum karbonat yüzdesi — halk dilinde 'kireç'. "
        "İç Anadolu'da topraklar genelde yüksek kireçlidir (%10–25). "
        "Kireç, çinko (Zn), demir (Fe) ve fosforu (P) bağlayarak bitkiye geçişini engeller — "
        "bu yüzden bölgede çinko eksikliği çok yaygındır."
    ),
    "Çinko (Zn)": (
        "Protein sentezi ve enzim üretimi için gerekli iz element. "
        "'İz element' demek çok az miktarda gerekli demek. "
        "Kritik eşik 0.5 ppm (çok küçük bir miktar). "
        "İç Anadolu'nun kireçli topraklarında Zn eksikliği çok yaygındır. "
        "Eksiklikte başak gelişimi durur, verim belirgin düşer."
    ),
    "Demir (Fe)": (
        "Klorofil üretimi ve nefes alma (solunum) için gerekli iz element. "
        "Eksikliğinde genç yapraklar sararır, damarcıklar yeşil kalır (kloroz). "
        "Yüksek kireçli alkali topraklarda Fe bitkiye geçemez; kritik eşik 4.5 ppm."
    ),
    "Bakır (Cu)": (
        "Fotosentez ve protein oluşumuna katkıda bulunan iz element. "
        "Kritik eşik 0.2 ppm. Eksikliği bölgede nadirdir."
    ),
    "Mangan (Mn)": (
        "Fotosentezde su molekülünü parçalayan enzimin temel bileşeni. "
        "Kritik eşik 1.0 ppm. Alkali kireçli topraklarda sınırda olabilir."
    ),
    "Bor (B)": (
        "Hücre büyümesi, tane bağlama ve şeker taşıması için gerekli iz element. "
        "İlginç bir özelliği: eksikliği de toksisitesi (zehirliliği) de zararlıdır — "
        "çok dar bir 'iyi aralık' vardır. "
        "İç Anadolu'nun bazı bölgelerinde toprakta bor fazlalığı görülür (>2 ppm dikkat)."
    ),
    "Katyon Değişim Kap. (CEC)": (
        "Toprağın besin maddelerini tutma kapasitesi. "
        "'Katyon' pozitif yüklü besin iyonları demek (K⁺, Ca²⁺, Mg²⁺, NH₄⁺ gibi). "
        "CEC yüksekse toprak besinleri uzun süre tutar, gübre kaybı az olur. "
        "me/100g birimi: 100 gram topraktaki yük kapasitesi. "
        "Killi ve kireçli topraklarda genelde yüksektir."
    ),
}

UNIT_TIPS: dict[str, str] = {
    "—":          "Birimsiz — 0 ile 14 arasında bir ölçek.",
    "%":          "Yüzde — 100 gram topraktaki gram miktarı.",
    "kg/da":      "Kilogram/dekar. Bir dekar 1.000 m² alandaki kilogram miktarı. (1 hektar = 10 dekar)",
    "ppm":        "Parts per million — milyonda bir parça. 1 ppm = 1 mg/kg = 1 gram/ton toprak. Çok küçük miktarları ifade eder.",
    "mg/kg":      "Miligram/kilogram = ppm. 1 kg topraktaki miligram miktarı. Mikro elementler bu birimle ölçülür.",
    "dS/m":       "DeciSiemens/metre — elektrik iletkenlik birimi. Topraktaki çözünmüş tuz yoğunluğunu gösterir.",
    "me/100g":    "Miliekivalent/100 gram. Toprağın besin iyonu tutma kapasitesini ölçer. cmol⁺/kg ile aynı şeydir.",
    "mg/kg (DTPA)": (
        "DTPA: topraktaki bitki tarafından alınabilir iz elementleri çıkarmak için kullanılan özel kimyasal çözelti. "
        "Laboratuvarda bu yöntemle ölçülen değer, bitkinin gerçekte ne kadar element alabileceğini gösterir. "
        "Birim: miligram/kilogram (ppm)."
    ),
}


def render_soil_table() -> None:
    """Toprak besin referans tablosunu Streamlit'e render eder."""
    rows = ""
    for r in SOIL_REFERENCE:
        low_txt   = f"&lt; {fmt(r.low_max)}" if r.low_max is not None else "—"
        high_txt  = f"&gt; {fmt(r.high_min)}" if r.high_min is not None else "—"
        ideal_txt = f"{fmt(r.ideal_low)} – {fmt(r.ideal_high)}"

        param_tip_text = PARAM_TIPS.get(r.name, "")
        unit_tip_text  = UNIT_TIPS.get(r.unit, "")

        param_html = tip(param_tip_text, r.name, wide=True) if param_tip_text else r.name
        unit_html  = tip(unit_tip_text, r.unit) if unit_tip_text else f"<span class='ref-unit'>{r.unit}</span>"

        rows += (
            f"<tr>"
            f"  <td><span class='ref-param'>{param_html}</span> "
            f"      <span class='ref-unit' style='margin-left:4px'>{unit_html}</span></td>"
            f"  <td class='ref-range' style='color:var(--ag-amber)'>{low_txt}</td>"
            f"  <td class='ref-ideal'>{ideal_txt}</td>"
            f"  <td class='ref-range' style='color:var(--ag-red)'>{high_txt}</td>"
            f"  <td class='ref-note'>{r.note}</td>"
            f"</tr>"
        )

    st.markdown(
        "<table class='ref-table'><thead><tr>"
        + th("Parametre", "Ölçülen toprak özelliğinin adı. Üzerine gelerek açıklamasını okuyabilirsin.", "18%")
        + th("Düşük / Yetersiz", "Bu değerin altındaysa toprakta eksiklik var demektir — bitki yeterince beslenemez.", "10%")
        + th("İdeal Aralık", "Buğday için en uygun değer aralığı. Toprak analizi bu aralıkta çıkarsa o parametre için sorun yok.", "13%")
        + th("Yüksek / Fazla", "Bu değerin üzerindeyse fazlalık var demektir — bazı elementler fazla olunca başka besinlerin alınmasını engeller.", "10%")
        + th("Açıklama", "İç Anadolu kıraç koşullarına özgü notlar ve dikkat edilmesi gerekenler.")
        + f"</tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )
    st.markdown(
        cap("Kaynaklar: TAGEM gübre tavsiye sistemi · Toprak Gübre ve Su Kaynakları Merkez Araştırma Enstitüsü · "
            "MEGEP toprak verimlilik standartları · Lindsay-Norvell DTPA kritik düzeyleri. "
            "Değerler referans/yorumlama amaçlıdır; kesin gübre dozu için parselden alınan güncel toprak analizi şarttır."),
        unsafe_allow_html=True,
    )
