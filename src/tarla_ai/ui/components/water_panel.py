"""Kuyu suyu referans paneli — kalıcı sulama kaynağı kaydı.

Dashboard'da her zaman görünür: pilot tarlanın tek sulama kaynağı olan
kuyu suyunun analiz değerlerini (su-analiz.pdf) FAO eşikleriyle karşılaştırır.
Ölçülmeyen parametreler "veri yok" olarak açıkça gösterilir — uydurulmaz.
"""

from __future__ import annotations

import streamlit as st

from tarla_ai.ui.components.explainer_box import render_explainer
from tarla_ai.ui.html import cap, fmt, section_head, th, tip, tip_attr
from tarla_ai.water.analysis import (
    STATUS_CAUTION,
    STATUS_OK,
    STATUS_SEVERE,
    STATUS_UNKNOWN,
    interpret_water,
)
from tarla_ai.water.reference import WELL_WATER_BASELINE, WELL_WATER_REPORT_META
from tarla_ai.water.validation import validate_water

_STATUS_COLOR = {
    STATUS_OK:      "var(--ag-accent)",
    STATUS_CAUTION: "var(--ag-amber)",
    STATUS_SEVERE:  "var(--ag-red)",
    STATUS_UNKNOWN: "var(--ag-line)",
}

# Su parametrelerinin sade-dil açıklamaları (mouse tooltip'i).
_PARAM_TIPS: dict[str, str] = {
    "pH": (
        "Suyun asit mi bazik mi olduğunu gösteren 0–14 ölçek. 7 nötr. "
        "Sulama suyu için ideal 6.5–8.4. Çok düşükse (asidik) damla sulama "
        "borularını aşındırabilir; kireçli toprakta etkisi büyük ölçüde tamponlanır."
    ),
    "EC (Tuzluluk)": (
        "Suyun elektrik iletkenliği — içindeki çözünmüş tuz miktarını gösterir. "
        "Tuz fazla olunca bitki kökten su çekemez, kurakmış gibi davranır. "
        "FAO: 0.7 altı sorunsuz, 0.7–3.0 dikkat, 3.0 üstü riskli. "
        "Bu kuyuda 2.90 dS/m — orta-yüksek; tekrarlı sulamada toprakta tuz birikir."
    ),
    "SAR (Sodyum Adsorpsiyon Oranı)": (
        "Sudaki sodyumun, kalsiyum ve magnezyuma oranı. Yüksekse sodyum toprağın "
        "kil tanelerini dağıtır; toprak sertleşir, su geçirmez hale gelir. "
        "Bu suda ÖLÇÜLMEMİŞ — Na, Ca, Mg gerektirir."
    ),
    "Sodyum (Na)": (
        "Sodyum iyonu. Yağmurlama sulamada yaprağı yakar, toprak yapısını bozar. "
        "Bu suda ÖLÇÜLMEMİŞ."
    ),
    "Klorür (Cl)": (
        "Klorür iyonu — bitki için toksik olabilen tuz bileşeni. Yüksek miktarda "
        "yaprak kenarlarını yakar. FAO: 140 mg/L altı sorunsuz, 350 üstü riskli. "
        "Bu suda ÖLÇÜLMEMİŞ."
    ),
    "Bikarbonat (HCO₃)": (
        "Sudaki bikarbonat. Yüksekse kalsiyumu çöktürüp SAR'ı yükseltir, "
        "damla sulama başlıklarını tıkar, yaprakta beyaz kireç lekesi yapar. "
        "Bu suda ÖLÇÜLMEMİŞ."
    ),
    "Bor (B)": (
        "Bitki için çok az gerekli ama fazlası zehirli olan iz element. Güvenli "
        "aralığı çok dar. Buğday/arpa ~2 mg/L'ye kadar dayanır. İç Anadolu'da yer "
        "yer bor fazlalığı görülür. Bu suda ÖLÇÜLMEMİŞ."
    ),
}

# Durum etiketi (pill) tooltip'leri.
_STATUS_TIPS: dict[str, str] = {
    STATUS_OK:      "Bu parametre sulama için uygun aralıkta — sorun yok.",
    STATUS_CAUTION: "Sınır değerlere yakın — dikkatli ve kontrollü kullan.",
    STATUS_SEVERE:  "Riskli seviye — bu parametre açısından kullanım kısıtlanmalı.",
    STATUS_UNKNOWN: "Laboratuvarda ölçülmemiş — değer bilinmiyor, tahmin edilmez.",
}

# Fenolojik dönem bazlı kullanım rehberi (ekim: Ekim ilk-ikinci hafta).
# Kuyu suyu EC=2.90 dS/m (orta-yüksek tuzluluk) için ihtiyatlı pencere.
_PHENOLOGY_GUIDE: tuple[tuple[str, str, str, str], ...] = (
    ("00–09", "Çimlenme", STATUS_CAUTION,
     "EC hassasiyeti en yüksek dönem. Mümkünse yağışa bırak; zorunluysa tek "
     "hafif sulama (20–30 mm), ardından yağış beklenmeli."),
    ("20–29", "Kardeşlenme", STATUS_OK,
     "Görece toleranslı dönem. Kış yağışı yoksa az-sık yerine fraksiyone "
     "sulama yapılabilir. Yıkama payı bırak."),
    ("—", "Kış durgunluğu (Ara–Şub)", STATUS_SEVERE,
     "Yağış dönemi; kuyu suyuna gerek yok, gereksiz tuz birikimi yapma."),
    ("30–39", "Sapa kalkma", STATUS_CAUTION,
     "Kritik büyüme + en yüksek su ihtiyacı. Tuz stresi verimi düşürür. "
     "Sulama öncesi toprak EC ölç; birikim varsa karıştırma/yıkama şart."),
    ("51–69", "Başaklanma–Çiçeklenme", STATUS_SEVERE,
     "Tuz stresi dane bağlamayı doğrudan etkiler. Bu suyla sulamadan kaçın."),
)


def _status_pill(status: str, label: str | None = None) -> str:
    color = _STATUS_COLOR.get(status, "inherit")
    text = (label or status).upper()
    tip_text = _STATUS_TIPS.get(status, "")
    return (
        f"<span class='stage-pill has-tip' data-tip=\"{tip_attr(tip_text)}\" "
        f"style='border:1px solid {color};color:{color}'>{text}</span>"
    )


def render_water_panel() -> None:
    """Kalıcı kuyu suyu referans panelini render eder."""
    st.markdown(
        section_head("Sulama Suyu Referansı — Kuyu (Kalıcı Kaynak Kaydı)"),
        unsafe_allow_html=True,
    )

    render_explainer(
        "Bu panel ne anlatıyor?",
        "Tarlayı sulayacağınız <b>kuyu suyunun</b>, buğday ve arpa için "
        "uygun olup olmadığını gösterir. En önemli iki şey şudur: "
        "<b>tuzluluk (EC)</b> — su çok tuzluysa bitki kökten su çekemez, "
        "kurakmış gibi davranır; ve <b>pH</b> — suyun asitlik derecesi. "
        "Tablodaki her satır bir su özelliğidir. Renkli etiket o özelliğin "
        "iyi mi yoksa riskli mi olduğunu söyler. <b>\"Veri yok\"</b> yazan "
        "satırlar laboratuvarda ölçülmemiştir — sistem bunları tahmin etmez, "
        "olduğu gibi \"bilinmiyor\" gösterir.",
        icon="💧",
        legend=(
            ("var(--ag-accent)", "uygun — sorun yok"),
            ("var(--ag-amber)", "dikkat — sınırlı kullan"),
            ("var(--ag-red)", "kısıtlı — kullanma"),
            ("var(--ag-line)", "veri yok — ölçülmemiş"),
        ),
    )

    report = WELL_WATER_BASELINE
    validation = validate_water(report)
    analysis = interpret_water(report)

    # ── Kaynak künyesi ────────────────────────────────────────
    meta = WELL_WATER_REPORT_META
    st.markdown(
        f'<div class="ag-card" style="display:grid;'
        f'grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:18px">'
        f'<div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Kaynak</div>'
        f'<div style="font-size:14px;font-weight:600">{meta["kaynak"]}</div></div>'
        f'<div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Konum</div>'
        f'<div style="font-size:14px;font-weight:600">{meta["konum"]}</div></div>'
        f'<div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Rapor</div>'
        f'<div style="font-size:14px;font-weight:600">'
        f'{meta["rapor_no"]} · {meta["onay_tarihi"]}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Genel uygunluk + veri-eksikliği bandı ─────────────────
    if not validation.has_minimum:
        st.markdown(
            '<div class="status-banner" style="border-left-color:var(--ag-red)">'
            '<div class="status-banner-title" style="color:var(--ag-red)">'
            'TEMEL VERİ EKSİK</div>'
            '<div class="status-banner-body">pH veya EC okunamadı — sulama '
            'uygunluğu değerlendirilemez.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        missing = ", ".join(validation.missing_full)
        st.markdown(
            f'<div class="status-banner" style="border-left-color:var(--ag-amber);'
            f'background:rgba(200,168,75,0.06);border-color:rgba(200,168,75,0.25)">'
            f'<div class="status-banner-title" style="color:var(--ag-amber)">'
            f'KISMİ VERİ — TAM RİSK DEĞERLENDİRMESİ YAPILAMADI</div>'
            f'<div class="status-banner-body">Mevcut rapor yalnızca '
            f'<b>pH + EC</b> içeriyor. Toprak yapısı (sodisite) ve toksisite '
            f'riski için gereken <b>{missing}</b> ÖLÇÜLMEMİŞ. Bu parametreler '
            f'"güvenli" varsayılmaz; tabloda "veri yok" olarak işaretlidir. '
            f'Tam karar için genişletilmiş su analizi gerekir.</div></div>',
            unsafe_allow_html=True,
        )

    # ── Parametre tablosu (ölçülen + ölçülmeyen) ──────────────
    rows = ""
    for p in analysis.results:
        color = _STATUS_COLOR.get(p.status, "inherit")
        val_txt = fmt(p.value) if p.value is not None else "—"
        tip_text = _PARAM_TIPS.get(p.name, "")
        param_html = tip(tip_text, p.name) if tip_text else p.name
        rows += (
            f"<tr>"
            f"  <td><span class='ref-param'>{param_html}</span> "
            f"      <span class='ref-unit' style='margin-left:4px'>{p.unit}</span></td>"
            f"  <td class='ref-ideal' style='color:{color}'>{val_txt}</td>"
            f"  <td>{_status_pill(p.status)}</td>"
            f"  <td class='ref-note'>{p.note}</td>"
            f"</tr>"
        )
    st.markdown(
        "<table class='ref-table'><thead><tr>"
        + th("Parametre",
             "Suyun ölçülen özelliği. Üzerine gelerek ne olduğunu okuyabilirsin.", "24%")
        + th("Ölçülen",
             "Laboratuvarda bu su örneğinde ölçülen değer. '—' ise ölçülmemiş.", "10%")
        + th("Durum",
             "Bu değerin sulama için uygun mu, riskli mi olduğunun renkli özeti.", "12%")
        + th("FAO Yorumu / Not",
             "Uluslararası FAO sulama suyu kılavuzuna göre açıklama ve dikkat notları.")
        + f"</tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )
    st.markdown(
        cap(f"Ölçülen parametre: {len(analysis.measured)} · "
            f"uygun: {analysis.ok_count} · dikkat: {analysis.caution_count} · "
            f"kısıtlı: {analysis.severe_count} · "
            f"ölçülmeyen: {len(analysis.unmeasured)}. "
            f"Eşikler FAO-29 (Ayers & Westcot) sulama suyu kılavuzundandır."),
        unsafe_allow_html=True,
    )

    # ── Fenolojik dönem kullanım rehberi ──────────────────────
    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        section_head("Kuyu Suyu — Fenolojik Dönem Kullanım Rehberi (BBCH)"),
        unsafe_allow_html=True,
    )
    render_explainer(
        "Hangi dönemde sulayabilirim?",
        "Buğday tohumdan başağa kadar belli aşamalardan geçer; bunlara "
        "<b>fenolojik dönem</b> denir (<b>BBCH</b>, bu dönemleri sayıyla "
        "kodlayan uluslararası bir ölçektir — 00 ekim, 89 hasat). "
        "Bu kuyu suyu tuzlu olduğu için <b>her dönemde verilemez</b>. "
        "Aşağıdaki tablo hangi aşamada suyun güvenle verilebileceğini "
        "(yeşil), ne zaman dikkatli olunması (sarı), ne zaman hiç "
        "verilmemesi (kırmızı) gerektiğini gösterir. Kısa kural: bu su "
        "günlük sulama için değil, sadece <b>kritik kuraklık anında "
        "kurtarma sulaması</b> içindir.",
        icon="🌱",
    )
    pheno_rows = ""
    for code, name, status, guide in _PHENOLOGY_GUIDE:
        label = {STATUS_OK: "KULLANILABİLİR",
                 STATUS_CAUTION: "DİKKATLİ",
                 STATUS_SEVERE: "KULLANMA"}.get(status, status.upper())
        pheno_rows += (
            f"<tr>"
            f"  <td class='ref-ideal' style='opacity:0.7'>{code}</td>"
            f"  <td><span class='ref-param'>{name}</span></td>"
            f"  <td>{_status_pill(status, label)}</td>"
            f"  <td class='ref-note'>{guide}</td>"
            f"</tr>"
        )
    st.markdown(
        "<table class='ref-table'><thead><tr>"
        + th("BBCH",
             "Büyüme döneminin uluslararası kod numarası (00 ekim → 89 hasat).", "10%")
        + th("Dönem", "Buğdayın gelişim aşamasının adı.", "22%")
        + th("Kuyu Suyu",
             "Bu dönemde kuyu suyu verilebilir mi? Yeşil=evet, sarı=dikkatli, "
             "kırmızı=hayır.", "16%")
        + th("Gerekçe", "Bu kararın tarımsal nedeni — neden bu dönemde uygun/riskli.")
        + f"</tr></thead><tbody>{pheno_rows}</tbody></table>",
        unsafe_allow_html=True,
    )
    st.markdown(
        cap("Ekim: Ekim ayı ilk–ikinci hafta. EC=2.90 dS/m orta-yüksek "
            "tuzluluk olduğundan kuyu suyu rutin değil, kritik dönem "
            "kurtarma sulaması olarak konumlandırılmıştır. Genel kural: "
            "salma değil damla/yağmurlama, yıkama payı bırak, sabah/akşam uygula."),
        unsafe_allow_html=True,
    )
