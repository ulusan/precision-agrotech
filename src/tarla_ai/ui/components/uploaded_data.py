"""Yüklenen gerçek veriyi işleyip gösteren bileşenler.

Toprak PDF → parse → doğrula → ölçülen vs referans karşılaştırması.
Drone GeoTIFF → analyze_scene → indeks/stres özeti.

Hiçbir değer uydurulmaz; parse edilemeyen alan "veri yok" gösterilir.
"""

from __future__ import annotations

import streamlit as st

from tarla_ai.drone.analysis import analyze_scene
from tarla_ai.soil.analysis import interpret_soil
from tarla_ai.soil.parsing import parse_soil_pdf_bytes
from tarla_ai.soil.validation import validate_soil
from tarla_ai.ui.components.explainer_box import render_explainer
from tarla_ai.ui.components.soil_table import PARAM_TIPS, UNIT_TIPS
from tarla_ai.ui.html import fmt, section_head, th, tip, tip_attr

_STATUS_COLOR = {
    "düşük":  "var(--ag-amber)",
    "ideal":  "var(--ag-accent)",
    "yüksek": "var(--ag-red)",
}

_STATUS_TIPS = {
    "düşük":  "Bu besin toprakta ideal aralığın altında — eksiklik olabilir, gübre gerekebilir.",
    "ideal":  "Bu besin buğday için uygun aralıkta — sorun yok.",
    "yüksek": "Bu değer ideal aralığın üstünde — fazlalık başka besinlerin alımını engelleyebilir.",
}


def render_uploaded_soil(pdf_bytes: bytes) -> None:
    """Yüklenen toprak PDF'ini parse edip ölçülen-vs-referans tablosu çizer."""
    st.markdown(section_head("Yüklenen Toprak Analizi — Ölçülen vs Referans"),
                unsafe_allow_html=True)

    render_explainer(
        "Bu panel ne anlatıyor?",
        "Laboratuvara gönderdiğiniz <b>toprak örneğinin</b> sonuçlarını "
        "okur ve buğday için <b>olması gereken ideal değerlerle</b> "
        "karşılaştırır. Toprakta hangi besin (azot, fosfor, çinko gibi) "
        "eksik, hangisi fazla — bunu görürsünüz. Her satırdaki renkli "
        "etiket sonucu özetler: <b>düşük</b> ise toprak o besin açısından "
        "fakir (gübre gerekebilir), <b>ideal</b> ise sorun yok, <b>yüksek</b> "
        "ise fazlalık var. PDF'ten okunamayan değerler tahmin edilmez; "
        "eksikse \"karar üretilmedi\" uyarısı çıkar."
        "<br><br>"
        "<b>Doğru numune nasıl alınır?</b> Tarlada farklı noktalarda "
        "0–20 cm derinliğinde çukurlar açılır; her noktadan alınan toprak "
        "temiz bir kovaya konur. <b>En az 10–12 farklı noktadan</b> numune "
        "alınmalıdır. Kovadaki topraklar iyice karıştırılır, karışımdan "
        "yaklaşık <b>2 kg</b> ayrılarak analize gönderilir. Taş, kök ve "
        "bitki artıkları numuneden çıkarılmalıdır.",
        icon="🧪",
        legend=(
            ("var(--ag-amber)", "düşük — eksik olabilir"),
            ("var(--ag-accent)", "ideal — sorun yok"),
            ("var(--ag-red)", "yüksek — fazla"),
        ),
    )

    report = parse_soil_pdf_bytes(pdf_bytes)
    validation = validate_soil(report)
    analysis = interpret_soil(report)

    # Karar-yeterlilik bandı
    if validation.is_decision_ready:
        st.markdown(
            '<div class="status-banner">'
            '<div class="status-banner-title">VERİ KARAR İÇİN YETERLİ</div>'
            '<div class="status-banner-body">Tüm zorunlu parametreler okundu. '
            'Aşağıda ölçülen değerler referans aralıklarıyla karşılaştırıldı.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        missing = ", ".join(validation.missing_required)
        st.markdown(
            f'<div class="status-banner" style="border-left-color:var(--ag-amber);'
            f'background:rgba(200,168,75,0.06);border-color:rgba(200,168,75,0.25)">'
            f'<div class="status-banner-title" style="color:var(--ag-amber)">'
            f'EKSİK ZORUNLU VERİ — KARAR ÜRETİLMEDİ</div>'
            f'<div class="status-banner-body">Şu zorunlu alanlar PDF\'ten okunamadı: '
            f'<b>{missing}</b>. Bu alanlar tamamlanmadan gübre/kireç önerisi üretilmez. '
            f'Okunabilen değerler aşağıda referansla karşılaştırıldı.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if not analysis.results:
        st.markdown(
            '<div style="opacity:0.6;font-size:13px">PDF\'ten hiçbir tanımlı parametre '
            'okunamadı. Raporun metin katmanlı (taranmış değil) olduğundan emin ol.</div>',
            unsafe_allow_html=True,
        )
        return

    rows = ""
    for p in analysis.results:
        color = _STATUS_COLOR.get(p.status, "inherit")
        param_tip = PARAM_TIPS.get(p.name, "")
        unit_tip = UNIT_TIPS.get(p.unit, "")
        param_html = tip(param_tip, p.name) if param_tip else p.name
        unit_html = tip(unit_tip, p.unit) if unit_tip else p.unit
        status_tip = _STATUS_TIPS.get(p.status, "")
        rows += (
            f"<tr>"
            f"  <td><span class='ref-param'>{param_html}</span> "
            f"      <span class='ref-unit' style='margin-left:4px'>{unit_html}</span></td>"
            f"  <td class='ref-ideal' style='color:{color}'>{fmt(p.value)}</td>"
            f"  <td><span class='stage-pill has-tip' data-tip=\"{tip_attr(status_tip)}\" "
            f"      style='border:1px solid {color};color:{color}'>"
            f"      {p.status.upper()}</span></td>"
            f"  <td class='ref-note'>{p.note}</td>"
            f"</tr>"
        )

    st.markdown(
        "<table class='ref-table'><thead><tr>"
        + th("Parametre",
             "Toprakta ölçülen besin/özellik. Üzerine gelerek ne işe yaradığını "
             "okuyabilirsin.", "22%")
        + th("Ölçülen", "Laboratuvarın bu toprak örneğinde ölçtüğü değer.", "12%")
        + th("Durum",
             "Bu değerin buğday için düşük mü, ideal mi, yüksek mi olduğunun renkli "
             "özeti.", "12%")
        + th("Açıklama", "İç Anadolu kıraç koşullarına özgü yorum ve dikkat notları.")
        + f"</tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="ag-cap">Okunan parametre: {len(analysis.results)} · '
        f'düşük: {analysis.low_count} · ideal: {analysis.ideal_count} · '
        f'yüksek: {analysis.high_count}. Değerler referans amaçlıdır; kesin doz için '
        f'agronomi danışmanına başvurun.</div>',
        unsafe_allow_html=True,
    )


def render_uploaded_drone(tiff_bytes: bytes) -> None:
    """Yüklenen GeoTIFF'i analiz edip indeks/stres özetini çizer."""
    st.markdown(section_head("Yüklenen Drone Görüntüsü — Sahne Analizi"),
                unsafe_allow_html=True)

    render_explainer(
        "Bu panel ne anlatıyor?",
        "Drone ile tarladan çekilen <b>havadan görüntüyü</b> analiz eder. "
        "İki tür görüntü olabilir: <b>RGB</b> (normal renkli fotoğraf) — "
        "bitki örtüsünün ne kadar yeşil/canlı olduğunu ölçer; ve "
        "<b>termal</b> (sıcaklık haritası) — bitkinin susuz kalıp "
        "kalmadığını gösterir. Susuz bitki terlemeyi keser ve <b>ısınır</b>; "
        "termal kamera bunu yakalar. <b>CWSI</b> denen değer 0'a yakınsa "
        "bitki rahat, 1'e yakınsa <b>su stresi</b> var demektir. Sıcak "
        "(stresli) bölgeler tarlada nerede sulama gerektiğini işaret eder.",
        icon="🛰️",
        legend=(
            ("var(--ag-accent)", "CWSI düşük — bitki rahat"),
            ("var(--ag-red)", "CWSI yüksek — susuz/stresli"),
        ),
    )

    result = analyze_scene(tiff_bytes)

    if result.raster_type == "unknown":
        st.markdown(
            '<div class="status-banner" style="border-left-color:var(--ag-red);'
            'background:rgba(217,80,48,0.06);border-color:rgba(217,80,48,0.25)">'
            '<div class="status-banner-title" style="color:var(--ag-red)">'
            'DOSYA TANINAMADI</div>'
            '<div class="status-banner-body">GeoTIFF ne RGB (3 bant) ne de termal '
            '(tek bant, °C) olarak tanındı. Termal dosya kalibre °C olarak '
            'export edilmeli; ham 16-bit DN tanınmaz.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    if result.raster_type == "thermal":
        if result.cwsi_mean is None:
            st.markdown(
                '<div style="opacity:0.6;font-size:13px">Termal dosya okundu ama sahne '
                'homojen (tek sıcaklık) — anlamlı ıslak/kuru referans yok, CWSI '
                'hesaplanamadı.</div>',
                unsafe_allow_html=True,
            )
            return
        _metric_grid([
            ("Tip", "Termal (LWIR)"),
            ("Ortalama CWSI", f"{result.cwsi_mean:.3f}"),
            ("Stresli alan oranı", f"%{result.stress_ratio * 100:.1f}"),
        ])
        st.markdown(
            '<div class="ag-cap">CWSI 0 = stres yok, 1 = ciddi su stresi. Referans '
            'sıcaklıklar aynı uçuştaki min/max pikselden alınır. Sulama kararı için '
            'referanstır, kesin reçete değildir.</div>',
            unsafe_allow_html=True,
        )
        return

    # RGB
    _metric_grid([
        ("Tip", "RGB (görünür)"),
        ("Ortalama VARI", f"{result.vari_mean:.3f}"),
        ("Ortalama TGI", f"{result.tgi_mean:.3f}"),
        ("Ortalama ExG", f"{result.exg_mean:.3f}"),
    ])
    st.markdown(
        '<div class="ag-cap">VARI/TGI/ExG görünür-bant yeşillik indeksleridir — '
        'NDVI DEĞİLDİR (RGB\'de NIR yok). NDVI/NDRE için Sentinel-2 verisi gerekir. '
        'Bu metrikler bitki örtüsü/canlılık hakkında referans verir.</div>',
        unsafe_allow_html=True,
    )


# Drone metriklerinin sade-dil açıklamaları (mouse tooltip'i).
_METRIC_TIPS: dict[str, str] = {
    "Tip": "Yüklenen görüntünün türü: RGB (renkli fotoğraf) veya termal (sıcaklık haritası).",
    "Ortalama CWSI": (
        "Crop Water Stress Index — bitki su stresi göstergesi. Termal görüntüden "
        "hesaplanır: susuz bitki terlemeyi kesip ısınır. 0'a yakın = bitki rahat, "
        "1'e yakın = ciddi susuzluk. Sulama gerekip gerekmediğinin ana sinyalidir."
    ),
    "Stresli alan oranı": (
        "Tarlanın yüzde kaçının su stresi altında olduğu. Yüksekse geniş bir alan "
        "susuz demektir; düşükse sadece küçük lekeler etkilenmiştir."
    ),
    "Ortalama VARI": (
        "Visible Atmospherically Resistant Index — normal renkli (RGB) fotoğraftan "
        "hesaplanan yeşillik göstergesi. Yüksek = daha yoğun/canlı bitki örtüsü. "
        "NDVI DEĞİLDİR (RGB'de kızılötesi bant yok)."
    ),
    "Ortalama TGI": (
        "Triangular Greenness Index — yapraktaki klorofil miktarına duyarlı görünür-bant "
        "yeşillik indeksi. Bitkinin ne kadar yeşil/sağlıklı olduğu hakkında fikir verir."
    ),
    "Ortalama ExG": (
        "Excess Green Index — görüntüdeki yeşil pikselleri toprak/artıktan ayıran indeks. "
        "Bitki örtüsünün kapladığı alanı tahmin etmekte kullanılır."
    ),
}


def _metric_grid(items: list[tuple[str, str]]) -> None:
    cells = []
    for label, value in items:
        tip_text = _METRIC_TIPS.get(label, "")
        label_html = tip(tip_text, label) if tip_text else label
        cells.append(
            f'<div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">{label_html}</div>'
            f'<div style="font-size:16px;font-weight:600">{value}</div></div>'
        )
    cols = "".join(cells)
    st.markdown(
        f'<div class="ag-card"><div style="display:grid;'
        f'grid-template-columns:repeat({len(items)},1fr);gap:18px">{cols}</div></div>',
        unsafe_allow_html=True,
    )
