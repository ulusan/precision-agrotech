"""Ne Yapmalı? paneli — bugünden ileriye, ekim öncesinden başlayan tarla serüveni.

Her aşama kartında DÖRT veri kaynağının (su / toprak / drone / hava) o aşamada
TOPRAĞA ve BİTKİYE ne yapılacağına katkısı gösterilir. Gerçek olan (hava, su)
somut kullanılır; toprak/drone yüklenince gerçek ölçümle dinamikleşir, yoksa
"yüklenince netleşir" denir — rastgele/dummy veri ASLA üretilmez.
"""

from __future__ import annotations

import streamlit as st

from tarla_ai.advisory.engine import AdvisoryContext, all_advice, build_context
from tarla_ai.advisory.models import OperationAdvice, SourceAction, Urgency
from tarla_ai.climate.reference import DEFAULT_LOCATION
from tarla_ai.drone.analysis import DroneAnalysis
from tarla_ai.soil.parsing import SoilReport
from tarla_ai.ui.components.climate_panel import _load_climate
from tarla_ai.ui.components.explainer_box import render_explainer
from tarla_ai.ui.html import section_head

_URGENCY_COLOR: dict[Urgency, str] = {
    Urgency.NOW:   "var(--ag-accent)",
    Urgency.WATCH: "var(--ag-amber)",
    Urgency.SOON:  "var(--ag-amber)",
    Urgency.DONE:  "var(--ag-line-2)",
    Urgency.INFO:  "var(--ag-line-2)",
}

_STATE_COLOR = {
    "baglandi":  "var(--ag-accent)",
    "yuklenince": "var(--ag-amber)",
    "beklemede": "var(--ag-line-2)",
}
_STATE_LABEL = {
    "baglandi":  "BAĞLI ✓",
    "yuklenince": "YÜKLENİNCE",
    "beklemede": "—",
}


def _read_uploads() -> tuple[bool, bool, SoilReport | None, DroneAnalysis | None]:
    """Soldaki panelden yüklenmiş toprak/drone dosyalarını oku ve gerçek değer için ayrıştır."""
    soil_obj: SoilReport | None = None
    drone_obj: DroneAnalysis | None = None
    soil_file = st.session_state.get("soil_pdf_upload")
    drone_file = st.session_state.get("geotiff_upload")
    has_soil = soil_file is not None
    has_drone = drone_file is not None
    if soil_file is not None:
        try:
            from tarla_ai.soil.parsing import parse_soil_pdf_bytes
            soil_obj = parse_soil_pdf_bytes(soil_file.getvalue())
        except Exception:
            soil_obj = None
    if drone_file is not None:
        try:
            from tarla_ai.drone.analysis import analyze_scene
            drone_obj = analyze_scene(drone_file.getvalue())
        except Exception:
            drone_obj = None
    return has_soil, has_drone, soil_obj, drone_obj


def _source_row(sa: SourceAction) -> str:
    c = _STATE_COLOR.get(sa.state, "var(--ag-line-2)")
    state_lbl = _STATE_LABEL.get(sa.state, sa.state)
    lines = ""
    if sa.toprak_action:
        lines += (f"<div style='font-size:12px;line-height:1.5;margin-top:3px'>"
                  f"<span style='opacity:0.55'>🌱 Toprağa:</span> {sa.toprak_action}</div>")
    if sa.bitki_action:
        lines += (f"<div style='font-size:12px;line-height:1.5;margin-top:3px'>"
                  f"<span style='opacity:0.55'>🌾 Bitkiye:</span> {sa.bitki_action}</div>")
    if sa.value_used:
        lines += (f"<div style='font-size:11px;color:var(--ag-accent);margin-top:3px'>"
                  f"✓ {sa.value_used}</div>")
    if sa.missing_note:
        lines += (f"<div style='font-size:11px;color:var(--ag-amber);margin-top:3px'>"
                  f"⤴ {sa.missing_note}</div>")
    return (
        f"<div style='border-left:2px solid {c};padding:6px 0 6px 12px;margin-bottom:8px'>"
        f"<div style='display:flex;align-items:center;gap:8px'>"
        f"<span style='font-size:13px;font-weight:600'>{sa.icon} {sa.label}</span>"
        f"<span class='stage-pill' style='border:1px solid {c};color:{c};font-size:9px'>"
        f"{state_lbl}</span></div>{lines}</div>"
    )


def _card(adv: OperationAdvice) -> str:
    c = _URGENCY_COLOR[adv.urgency]
    glow = "box-shadow:0 0 0 1px rgba(93,184,42,0.25);" if adv.urgency == Urgency.NOW else ""
    flex = "display:flex;justify-content:space-between;align-items:flex-start;gap:12px"
    eta = f"<span style='opacity:0.55'>· {adv.eta}</span>" if adv.eta else ""
    sources = "".join(_source_row(s) for s in adv.source_actions)
    return (
        f"<div class='ag-card' style='border-left:3px solid {c};margin-bottom:14px;{glow}'>"
        f"  <div style='{flex}'>"
        f"    <div style='font-size:16px;font-weight:600'>{adv.icon}&nbsp; {adv.title}</div>"
        f"    <span class='stage-pill' style='border:1px solid {c};color:{c}'>"
        f"      {adv.urgency_label}</span>"
        f"  </div>"
        f"  <div style='font-size:11px;opacity:0.5;margin:4px 0 12px;letter-spacing:0.04em;"
        f"             text-transform:uppercase'>⏱ {adv.timing} {eta}</div>"
        f"  <div style='font-size:14px;font-weight:600;line-height:1.55;"
        f"             color:var(--ag-accent);margin-bottom:8px'>▶ {adv.headline}</div>"
        f"  <div style='font-size:13px;opacity:0.78;line-height:1.65;margin-bottom:14px'>"
        f"    {adv.detail}</div>"
        f"  <div style='font-size:10px;font-weight:600;letter-spacing:0.12em;"
        f"             text-transform:uppercase;opacity:0.45;margin-bottom:8px'>"
        f"    Veri kaynakları → toprağa / bitkiye eylem</div>"
        f"  {sources}"
        f"</div>"
    )


def _readiness_strip(ctx: AdvisoryContext) -> str:
    def chip(label: str, ok: bool, ok_txt: str, no_txt: str) -> str:
        c = "var(--ag-accent)" if ok else "var(--ag-amber)"
        return (f"<div style='flex:1;min-width:150px;border:1px solid {c};border-radius:8px;"
                f"padding:10px 14px'><div style='font-size:12px;font-weight:600;color:{c}'>"
                f"{label}</div><div style='font-size:11px;opacity:0.65;margin-top:2px'>"
                f"{ok_txt if ok else no_txt}</div></div>")
    ec = ctx.water_ec_ds_m
    return (
        "<div style='display:flex;gap:10px;flex-wrap:wrap;margin:4px 0 18px'>"
        + chip("🌤️ Hava durumu", True, "Bağlı — Open-Meteo (gerçek veri)", "")
        + chip("💧 Su analizi", ec is not None,
               f"Bağlı — kuyu kaydı (EC {ec:.2f})" if ec is not None else "", "Yok")
        + chip("🧪 Toprak analizi", ctx.has_soil,
               "Yüklendi — gerçek değerler işleniyor", "Bekleniyor — PDF yükle")
        + chip("🛰️ Drone görüntüsü", ctx.has_drone,
               "Yüklendi — sahne analizi işleniyor", "Bekleniyor — GeoTIFF yükle")
        + "</div>"
    )


def render_advisory_panel() -> None:
    """Ne Yapmalı? panelinin tüm içeriğini render eder."""
    loc = DEFAULT_LOCATION
    yer = loc.label.split("—")[-1].strip()
    st.markdown(section_head(f"Ne Yapmalı? — Buğday Tarla Serüveni ({yer})"),
                unsafe_allow_html=True)

    render_explainer(
        "Bu sayfa nasıl çalışıyor?",
        "Tarla <b>henüz ekilmedi</b>; burası bugünden başlayıp hasada kadar ilerleyen "
        "bir <b>yol haritasıdır</b>. Her aşamada <b>dört veri kaynağının</b> "
        "(💧 su analizi, 🧪 toprak analizi, 🛰️ drone, 🌤️ hava) o işte <b>toprağa ve "
        "bitkiye ne yapılacağına</b> nasıl katkı verdiğini ayrı ayrı görürsün.<br><br>"
        "İki tür veri var: <b>otomatik bağlı olanlar</b> (hava Open-Meteo'dan, su "
        "kuyu kaydından — gerçek) ve <b>senin yükleyeceklerin</b> (toprak analizi, "
        "drone). Bir veri yoksa kart bunu açıkça söyler ve <b>asla uydurmaz</b>; "
        "yüklediğinde o aşamanın önerisi senin tarlanın gerçek ölçümleriyle güncellenir.",
        icon="🧭",
        legend=(
            ("var(--ag-accent)", "bağlı / gerçek veri var"),
            ("var(--ag-amber)", "yüklenince netleşir"),
            ("var(--ag-line-2)", "bu aşamada gerekli değil"),
        ),
        expanded=True,
    )

    with st.spinner("Pilot tarla hava verisi yükleniyor…"):
        days = _load_climate(loc.lat, loc.lon)
    if not days:
        st.warning("⚠️ Hava verisine ulaşılamadı; öneriler şu an üretilemiyor. "
                   "Birkaç dakika sonra tekrar dene.", icon="🌐")
        return

    has_soil, has_drone, soil, drone = _read_uploads()
    ctx = build_context(days, has_soil=has_soil, has_drone=has_drone, soil=soil, drone=drone)
    advices = all_advice(days, has_soil=has_soil, has_drone=has_drone, soil=soil, drone=drone)

    st.markdown(
        f'<div class="status-banner">'
        f'  <div class="status-banner-title">📍 BUGÜN: {ctx.today.strftime("%d.%m.%Y")} '
        f'  — TARLA HENÜZ EKİLMEDİ (EKİM ÖNCESİ)</div>'
        f'  <div class="status-banner-body">'
        f'  Ekim penceresine <b>~{ctx.days_to_sowing} gün</b> var '
        f'  (tahmini ekim: {ctx.next_sowing.strftime("%d.%m.%Y")} civarı). '
        f'  Şimdiki öncelik: <b>toprak analizi yaptırıp yüklemek</b> ve tarla hazırlığı.<br>'
        f'  <span style="opacity:0.7">Tarla: {yer} ({loc.lat:.4f}, {loc.lon:.4f}) '
        f'  · kıraç (kuru tarım) · kışlık ekmeklik buğday</span></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(_readiness_strip(ctx), unsafe_allow_html=True)
    st.markdown("".join(_card(a) for a in advices), unsafe_allow_html=True)

    st.markdown(
        '<div class="ag-cap">Tarihler tipik Ankara/Bala kıraç buğday takvimine ve pilot '
        'tarlanın gerçek hava verisine dayanır; yıl koşullarına göre ±10 gün kayabilir. '
        'Doz aralıkları (kg N/da, sıra arası vb.) bölgesel referanstır (TAGEM/FAO); kesin '
        'değerler toprak analizi yüklenince ölçüme göre kişiselleşir.</div>',
        unsafe_allow_html=True,
    )
