"""Pilot Tarla Dashboard — Ankara/Bala kıraç ekmeklik buğday referans paneli.

Bu dashboard henüz EKİM ÖNCESİ aşamadadır. Toprak analizi ve drone görüntüleri
henüz elde edilmemiştir. Panel, buğday için olması gereken REFERANS değerleri
gösterir; veri yüklendiğinde ölçülen değerler bu referanslarla karşılaştırılır.

Çalıştır:  uv run streamlit run app.py
"""

from __future__ import annotations

import base64
from pathlib import Path

import fitz  # pymupdf
import streamlit as st

from tarla_ai.reference import (
    GROWTH_STAGES,
    NITROGEN_SUMMARY,
    SOIL_REFERENCE,
)

# ── Sayfa yapılandırması ─────────────────────────────────
st.set_page_config(
    page_title="Tarla Referans Paneli — Ulusan AgroTech",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════
# STİL — config.toml tema renklerini MİRAS ALIR.
# ════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&display=swap');

:root {
  --ag-accent:  #5db82a;
  --ag-amber:   #c8a84b;
  --ag-red:     #d95030;
  --ag-line:    rgba(255,255,255,0.08);
  --ag-line-2:  rgba(255,255,255,0.12);
  --ag-fill:    rgba(255,255,255,0.04);
  --ag-tip-bg:  rgba(15,15,15,0.96);
}

html, body,
.stApp p, .stApp span, .stApp label, .stApp li,
.stApp td, .stApp th, .stApp h1, .stApp h2, .stApp h3,
.stApp button, .stApp input, .stApp a,
[class*="ag-"], [class*="mc-"], [class*="sb-"],
[class*="rec-"], [class*="bbch-"], [class*="soil-"], [class*="ref-"], .has-tip, .tip {
  font-family: 'Space Grotesk', system-ui, sans-serif;
}
[class*="material-symbols"],
.material-symbols-rounded,
[data-testid] span[translate="no"] {
  font-family: 'Material Symbols Rounded' !important;
}

[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] *,
[data-testid="stExpandSidebarButton"],
[data-testid="stExpandSidebarButton"] * {
  opacity: 1 !important;
  visibility: visible !important;
}

[data-testid="stDivider"] hr {
  border-color: var(--ag-line) !important;
  margin: 12px 0 !important;
}

/* ── Sidebar / section başlıkları ── */
.sb-head {
  font-size: 9px; font-weight: 600; letter-spacing: 0.14em;
  text-transform: uppercase; opacity: 0.5; margin-bottom: 8px;
}
.ag-head {
  font-size: 10px; font-weight: 600; letter-spacing: 0.16em;
  text-transform: uppercase; opacity: 0.55;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--ag-line);
  margin-bottom: 18px;
}
.ag-hint { font-size: 11px; opacity: 0.45; margin-top: 10px; margin-bottom: 28px; }
.ag-cap  { font-size: 11px; opacity: 0.5; line-height: 1.5; margin-top: 6px; }

.ag-card {
  background: var(--ag-fill);
  border: 1px solid var(--ag-line-2);
  padding: 18px 20px;
}

/* ── Durum bandı (ekim öncesi bilgilendirme) ── */
.status-banner {
  background: rgba(93,184,42,0.06);
  border: 1px solid rgba(93,184,42,0.25);
  border-left: 3px solid var(--ag-accent);
  padding: 16px 20px; margin-bottom: 28px;
}
.status-banner-title {
  font-size: 12px; font-weight: 600; letter-spacing: 0.06em;
  color: var(--ag-accent); margin-bottom: 6px;
}
.status-banner-body { font-size: 13px; line-height: 1.6; opacity: 0.8; }

/* ── Referans tablosu ── */
.ref-table { width: 100%; border-collapse: collapse; }
.ref-table th {
  font-size: 10px; font-weight: 600; letter-spacing: 0.12em;
  text-transform: uppercase; opacity: 0.5;
  padding: 8px 12px;
  border-bottom: 1px solid var(--ag-line);
  text-align: left;
}
.ref-table td {
  padding: 11px 12px;
  border-bottom: 1px solid var(--ag-line);
  vertical-align: top; font-size: 13px; line-height: 1.5;
}
.ref-table tr:last-child td { border-bottom: none; }
.ref-ideal {
  font-variant-numeric: tabular-nums; font-weight: 600;
  color: var(--ag-accent); white-space: nowrap;
}
.ref-range {
  font-variant-numeric: tabular-nums; font-size: 12px; opacity: 0.7;
  white-space: nowrap;
}
.ref-note { font-size: 12px; opacity: 0.6; line-height: 1.5; }
.ref-param { font-weight: 600; }
.ref-unit { font-size: 11px; opacity: 0.5; font-weight: 400; }

/* ── Büyüme dönemi tablosu ── */
.stage-pill {
  display: inline-block; font-size: 10px; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase;
  padding: 2px 9px; border-radius: 3px;
}
.stage-pill-low    { border: 1px solid var(--ag-line-2); color: rgba(232,232,232,0.6); }
.stage-pill-mid    { border: 1px solid var(--ag-amber); color: var(--ag-amber); }
.stage-pill-high   { border: 1px solid var(--ag-red); color: var(--ag-red); }

/* ── Tooltip ── */
.has-tip { cursor: help; border-bottom: 1px dashed rgba(128,128,128,0.4); position: relative; }
.has-tip .tip {
  visibility: hidden; opacity: 0; pointer-events: none;
  position: absolute; z-index: 300;
  left: 0; top: calc(100% + 8px); width: 270px;
  background: var(--ag-tip-bg);
  border: 1px solid var(--ag-line-2);
  padding: 11px 14px;
  font-size: 12.5px; color: #e8e8e8 !important; line-height: 1.6;
  font-weight: 400; letter-spacing: 0; text-transform: none;
  transition: opacity 0.15s;
  backdrop-filter: blur(12px);
}
.has-tip:hover .tip { visibility: visible; opacity: 1; }

/* ── BBCH Diyagram ── */
.bbch-track {
  display: flex; align-items: flex-start; gap: 0;
  width: 100%; overflow-x: auto; padding-bottom: 4px;
}
.bbch-stage {
  flex: 1; min-width: 80px;
  display: flex; flex-direction: column; align-items: center;
  position: relative;
}
.bbch-stage:not(:last-child)::after {
  content: ""; position: absolute; top: 19px; left: 50%;
  width: 100%; height: 1px;
  background: var(--ag-line); z-index: 0;
}
.bbch-dot {
  width: 38px; height: 38px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; letter-spacing: -0.02em;
  position: relative; z-index: 1;
  border: 1px solid transparent; transition: transform 0.15s;
}
.bbch-dot-future   { background: rgba(128,128,128,0.06); border-color: rgba(128,128,128,0.15); opacity: 0.55; }
.bbch-dot-start    { background: var(--ag-accent); border-color: var(--ag-accent); color: #06200a; box-shadow: 0 0 0 4px rgba(93,184,42,0.2); }
.bbch-dot-selected { outline: 2px solid #e8e8e8; outline-offset: 3px; }
.bbch-label {
  font-size: 10px; font-weight: 600; letter-spacing: 0.04em;
  margin-top: 9px; text-align: center; line-height: 1.3; padding: 0 4px;
}
.bbch-label-future { opacity: 0.4; }
.bbch-label-start  { color: var(--ag-accent) !important; opacity: 1; }

/* ── BBCH Detay Paneli ── */
.bbch-detail {
  margin-top: 20px;
  background: var(--ag-fill);
  border: 1px solid var(--ag-line-2);
  padding: 20px 24px;
}
.bbch-detail-code {
  font-size: 11px; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; opacity: 0.5; margin-bottom: 4px;
}
.bbch-detail-title { font-size: 18px; font-weight: 600; margin-bottom: 14px; }
.bbch-detail-body { font-size: 13px; line-height: 1.7; opacity: 0.85; }
.bbch-detail-tasks { margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--ag-line); }
.bbch-detail-tasks-head {
  font-size: 10px; font-weight: 700; letter-spacing: 0.14em;
  text-transform: uppercase; opacity: 0.45; margin-bottom: 10px;
}
.bbch-task-item { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px; font-size: 13px; }
.bbch-task-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }
.bbch-task-dot-green  { background: var(--ag-accent); }
.bbch-task-dot-amber  { background: var(--ag-amber); }
.bbch-task-dot-red    { background: var(--ag-red); }

[class*="bbch-btn"] button,
.bbch-track ~ div [data-testid="stButton"] button {
  background: transparent !important;
  border: 1px solid var(--ag-line) !important;
  color: rgba(232,232,232,0.35) !important;
  font-size: 10px !important;
  padding: 2px 0 !important;
  min-height: 24px !important;
  border-radius: 4px !important;
  transition: border-color 0.15s, color 0.15s !important;
}
[class*="bbch-btn"] button:hover,
.bbch-track ~ div [data-testid="stButton"] button:hover {
  border-color: var(--ag-accent) !important;
  color: var(--ag-accent) !important;
  background: rgba(93,184,42,0.06) !important;
}

/* ── PDF ── */
.pdf-wrap { border: 1px solid var(--ag-line-2); }
.pdf-wrap img { display: block; width: 100%; }
</style>
""", unsafe_allow_html=True)


# ── Yardımcılar ──────────────────────────────────────────
def section_head(label: str) -> str:
    return f'<div class="ag-head">{label}</div>'

def sidebar_head(label: str) -> str:
    return f'<div class="sb-head">{label}</div>'

def cap(text: str) -> str:
    return f'<div class="ag-cap">{text}</div>'


# ════════════════════════════════════════════════════════
# PDF ÖNBELLEĞI
# ════════════════════════════════════════════════════════
@st.cache_data
def load_pdf_pages(pdf_path: str, dpi_scale: float = 1.6) -> list[str]:
    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(dpi_scale, dpi_scale)
    pages: list[str] = []
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pages.append(base64.b64encode(pix.tobytes("png")).decode())
    doc.close()
    return pages

PDF_PATH  = Path(__file__).parent / "ulusan-agrotech-solutions.pdf"
pdf_pages = load_pdf_pages(str(PDF_PATH)) if PDF_PATH.exists() else []

if "pdf_idx" not in st.session_state:
    st.session_state["pdf_idx"] = 0


# ════════════════════════════════════════════════════════
# SIDEBAR — Veri Yükleme (ileride kullanılacak)
# ════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div style="font-size:15px;font-weight:600;margin-bottom:2px">Tarla Referans Paneli</div>'
        '<div style="font-size:11px;opacity:0.55;margin-bottom:16px">Ulusan AgroTech Solutions</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown(sidebar_head("Veri Yükle"), unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:11px;opacity:0.5;line-height:1.6;margin-bottom:12px">'
        'Toprak analizi ve drone görüntüleri elde edildiğinde buradan yüklenecek. '
        'Yüklenen değerler aşağıdaki referans aralıklarıyla karşılaştırılacak.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.file_uploader(
        "Toprak analiz raporu (PDF)",
        type=["pdf"], disabled=True,
        help="Henüz toprak analizi yapılmadı. Lab raporu hazır olduğunda aktif olacak.",
        key="soil_pdf_upload",
    )
    st.file_uploader(
        "Drone görüntüsü (GeoTIFF)",
        type=["tif", "tiff"], disabled=True,
        help="Henüz uçuş yapılmadı. Termal/RGB GeoTIFF hazır olduğunda aktif olacak.",
        key="geotiff_upload",
    )
    st.divider()
    st.markdown(
        '<div style="font-size:11px;opacity:0.45;line-height:1.6">'
        'Tarla: Ankara · Bala<br>Ürün: Kışlık ekmeklik buğday<br>Sistem: Kıraç (kuru tarım)<br>'
        'Durum: Ekim öncesi'
        '</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════
# BAŞLIK
# ════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;justify-content:space-between;align-items:flex-end;'
    'border-bottom:1px solid var(--ag-line);padding-bottom:20px;margin-bottom:28px">'
    '  <div>'
    '    <div style="font-size:10px;font-weight:600;letter-spacing:0.18em;'
    '                text-transform:uppercase;opacity:0.5;margin-bottom:8px">'
    '      Ulusan AgroTech Solutions &nbsp;·&nbsp; Proje Raporu 2026</div>'
    '    <div style="font-size:26px;font-weight:600;letter-spacing:-0.02em;line-height:1.15">'
    '      Pilot Tarla &mdash; Buğday Besin Referans Paneli</div>'
    '    <div style="font-size:13px;opacity:0.55;margin-top:8px">'
    '      Ankara &middot; Bala &nbsp;&middot;&nbsp; Kışlık ekmeklik buğday'
    '      &nbsp;&middot;&nbsp; İç Anadolu kıraç koşulları'
    '    </div>'
    '  </div>'
    '  <div style="text-align:right;font-size:12px;opacity:0.6;line-height:2">'
    '    <div style="font-size:16px;font-weight:600;opacity:1;letter-spacing:-0.01em">'
    '      Ekim Öncesi</div>'
    '    Veri toplama başlamadı'
    '  </div>'
    '</div>',
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════
# DURUM BANDI
# ════════════════════════════════════════════════════════
st.markdown(
    '<div class="status-banner">'
    '  <div class="status-banner-title">EKİM ÖNCESİ — VERİ BEKLENİYOR</div>'
    '  <div class="status-banner-body">'
    '    Tarlaya henüz ekim yapılmadı; toprak analizi ve drone görüntüleri elde edilmedi. '
    '    Bu panel, Ankara/Bala kıraç koşullarında ekmeklik buğday için <b>olması gereken '
    '    referans değerleri</b> gösterir. Toprak analizi ve drone uçuşları yapıldığında, '
    '    ölçülen değerler bu tablolarla karşılaştırılarak gübre/sulama kararları üretilecektir.'
    '  </div>'
    '</div>',
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════
# TABLO 1 — TOPRAK BESİN REFERANS ARALIKLARI
# ════════════════════════════════════════════════════════
st.markdown(section_head("Toprak Besin Referans Aralıkları — Buğday (Ankara/Bala Kıraç)"),
            unsafe_allow_html=True)

def _fmt(v: float) -> str:
    return f"{v:g}"

ref_rows = ""
for r in SOIL_REFERENCE:
    low_txt  = f"&lt; {_fmt(r.low_max)}" if r.low_max is not None else "—"
    high_txt = f"&gt; {_fmt(r.high_min)}" if r.high_min is not None else "—"
    ideal_txt = f"{_fmt(r.ideal_low)} – {_fmt(r.ideal_high)}"
    ref_rows += (
        f"<tr>"
        f"  <td><span class='ref-param'>{r.name}</span> "
        f"      <span class='ref-unit'>{r.unit}</span></td>"
        f"  <td class='ref-range' style='color:var(--ag-amber)'>{low_txt}</td>"
        f"  <td class='ref-ideal'>{ideal_txt}</td>"
        f"  <td class='ref-range' style='color:var(--ag-red)'>{high_txt}</td>"
        f"  <td class='ref-note'>{r.note}</td>"
        f"</tr>"
    )

st.markdown(
    "<table class='ref-table'>"
    "  <thead><tr>"
    "    <th style='width:18%'>Parametre</th>"
    "    <th style='width:10%'>Düşük / Yetersiz</th>"
    "    <th style='width:13%'>İdeal Aralık</th>"
    "    <th style='width:10%'>Yüksek / Fazla</th>"
    "    <th>Açıklama (İç Anadolu kıraç buğday)</th>"
    "  </tr></thead>"
    f"  <tbody>{ref_rows}</tbody>"
    "</table>",
    unsafe_allow_html=True,
)
st.markdown(
    cap("Kaynaklar: TAGEM gübre tavsiye sistemi · Toprak Gübre ve Su Kaynakları Merkez Araştırma Enstitüsü · "
        "MEGEP toprak verimlilik standartları · Lindsay-Norvell DTPA kritik düzeyleri. "
        "Değerler referans/yorumlama amaçlıdır; kesin gübre dozu için parselden alınan güncel toprak analizi şarttır."),
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-top:36px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# TABLO 2 — BÜYÜME DÖNEMİNE GÖRE N/SU İHTİYACI
# ════════════════════════════════════════════════════════
st.markdown(section_head("Büyüme Dönemine Göre Azot ve Su İhtiyacı — Kıraç Buğday"),
            unsafe_allow_html=True)

def _n_pill(seviye: str) -> str:
    s = seviye.lower()
    if "pik" in s or "yüksek" in s:
        cls = "stage-pill-high"
    elif "orta" in s:
        cls = "stage-pill-mid"
    else:
        cls = "stage-pill-low"
    return f'<span class="stage-pill {cls}">{seviye}</span>'

stage_rows = ""
for s in GROWTH_STAGES:
    stage_rows += (
        f"<tr>"
        f"  <td><span class='ref-param'>{s.donem}</span><br>"
        f"      <span class='ref-unit'>BBCH {s.bbch}</span></td>"
        f"  <td>{_n_pill(s.n_seviye)}</td>"
        f"  <td class='ref-range' style='color:var(--ag-accent)'>{s.n_doz}</td>"
        f"  <td class='ref-note'>{s.su_ihtiyaci}</td>"
        f"  <td class='ref-note'>{s.note}</td>"
        f"</tr>"
    )

st.markdown(
    "<table class='ref-table'>"
    "  <thead><tr>"
    "    <th style='width:16%'>Dönem</th>"
    "    <th style='width:12%'>Azot İhtiyacı</th>"
    "    <th style='width:16%'>Öneri (kıraç)</th>"
    "    <th style='width:16%'>Su İhtiyacı</th>"
    "    <th>Kritik Not</th>"
    "  </tr></thead>"
    f"  <tbody>{stage_rows}</tbody>"
    "</table>",
    unsafe_allow_html=True,
)

# Azot özeti kartı
st.markdown(
    f'<div class="ag-card" style="margin-top:18px">'
    f'  <div style="font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;'
    f'              opacity:0.55;margin-bottom:12px">Toplam Azot Programı Özeti (Kıraç)</div>'
    f'  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:18px">'
    f'    <div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Taban (ekimle)</div>'
    f'         <div style="font-size:15px;font-weight:600">{NITROGEN_SUMMARY["taban_N_kgda"]}</div></div>'
    f'    <div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Üst gübre</div>'
    f'         <div style="font-size:15px;font-weight:600">{NITROGEN_SUMMARY["ust_gubre_kurac"]}</div></div>'
    f'    <div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Toplam N</div>'
    f'         <div style="font-size:15px;font-weight:600;color:var(--ag-accent)">{NITROGEN_SUMMARY["toplam_N_kurac"]}</div></div>'
    f'    <div><div style="font-size:11px;opacity:0.5;margin-bottom:4px">Fosfor (P₂O₅) taban</div>'
    f'         <div style="font-size:15px;font-weight:600">{NITROGEN_SUMMARY["P2O5_taban"]}</div></div>'
    f'  </div>'
    f'  <div style="font-size:12px;opacity:0.6;line-height:1.6;margin-top:14px;'
    f'              border-top:1px solid var(--ag-line);padding-top:12px">{NITROGEN_SUMMARY["not"]}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-top:36px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# BBCH FENOLOJİK AŞAMA DİYAGRAMI (referans takvim)
# ════════════════════════════════════════════════════════
# (kod, ad, açıklama, kısa_etiket, görevler)
BBCH_STAGES = [
    ("00", "Çimlenme", "Ekim — Çimlenme",
     "Tohum toprağa verilir; su alımıyla şişme ve çimlenme başlar. "
     "Toprak nemi homojen olmalı, ekim derinliği 3–5 cm idealdir.",
     [("green", "Tohum yatağı hazırlığını kontrol et"),
      ("green", "Ekim derinliğini 3–5 cm ayarla"),
      ("green", "Tüm fosforu (6–8 kg/da) ekimle taban gübresi olarak ver"),
      ("amber", "Çinko eksikse çinkolu DAP kullan")]),

    ("10", "Çıkış", "Çıkış",
     "İlk yaprak toprak yüzeyini deler; bitki fotosenteze başlar. "
     "Çıkış oranı ve homojenliği verim tahmini için kritik veridir.",
     [("green", "Çıkış sayımı yap ve homojenliği değerlendir"),
      ("green", "Yabancı ot baskısını kontrol et"),
      ("amber", "Erken don riski varsa önlem al"),
      ("amber", "Çıkış oranını kaydet (%)")]),

    ("20", "Kardeşlenme", "Kardeşlenme",
     "Ana sapın yanında yeni yan saplar (kardeş) oluşur. "
     "Kardeş sayısı verim potansiyelini doğrudan belirler; "
     "azot ihtiyacı bu dönemde artmaya başlar.",
     [("green", "Kardeş sayısını say (hedef: 3–5 kardeş/bitki)"),
      ("red",   "1. üst gübre azot uygula (2–4 kg N/da) — yağış öncesi"),
      ("amber", "Herbisit uygulaması için uygun pencereyi belirle"),
      ("amber", "Kışlık ekimde don zararını kontrol et")]),

    ("30", "Sapa Kalkma", "Sapa Kalkma",
     "Bitki boyunu hızla artırır; boğumlar birbirinden uzaklaşır. "
     "Azot ve su ihtiyacı bu evrede en yüksek noktadadır. "
     "Bu dönemdeki kuraklık verimi en çok düşürür.",
     [("red",   "2. üst gübre azot uygula (2–3 kg N/da)"),
      ("red",   "Su stresini izle — en kritik su dönemi"),
      ("amber", "Yatma riskine karşı büyüme düzenleyici değerlendir"),
      ("green", "Fungisit ihtiyacını değerlendir")]),

    ("37", "Bayrak Yaprak", "Bayrak Yaprak",
     "Son yaprak (bayrak yaprağı) açılır; bu yaprak tane dolumunun "
     "ana fotosentez kaynağıdır. Azot alımı en üst düzeydedir.",
     [("red",   "Bayrak yaprağı hastalıklarını (pas, septoria) izle"),
      ("amber", "Gerekirse yapraktan üre/Zn takviyesi (protein için)"),
      ("green", "Yaprak alan indeksini değerlendir"),
      ("green", "Su durumunu kontrol et")]),

    ("51", "Başaklanma", "Başaklanma",
     "Başak yaprak kılıfından çıkmaya başlar. Hastalık baskısının "
     "arttığı dönemdir; özellikle sarı pas ve septoria izlenmelidir.",
     [("red",   "Fungisit uygulaması — sarı pas ve septoria"),
      ("amber", "Başak gelişimini ve homojenliği izle"),
      ("green", "Yaprak alan indeksini değerlendir"),
      ("amber", "Dolu ve aşırı yağış riskini takip et")]),

    ("65", "Çiçeklenme", "Çiçeklenme",
     "Başağın yarısından fazlasında çiçeklenme tamamlanmıştır. "
     "Su stresine en hassas dönemdir; fusarium riski maksimuma ulaşır.",
     [("red",   "Fusarium'a karşı fungisit uygula — kritik pencere"),
      ("red",   "Su stresini izle — döllenmeyi doğrudan etkiler"),
      ("amber", "Sıcaklık + nem kombinasyonunu izle (fusarium)"),
      ("green", "Çiçeklenme homojenliğini kaydet")]),

    ("75", "Tane Dolumu", "Tane Dolumu",
     "Daneler dolar; süt ve hamur olum aşamalarından geçer. "
     "Su ve sıcaklık stresi dane ağırlığını düşürür.",
     [("amber", "Dane dolum hızını izle"),
      ("amber", "Geç dönem yapraktan üre — tane proteini için"),
      ("green", "Kuş ve zararlı baskısını kontrol et"),
      ("green", "Hasat ekipmanı bakımını planla")]),

    ("89", "Sarı Olum", "Sarı Olum",
     "Daneler sarılaşır, nem düşer. Hasat zamanlaması ve lojistiği "
     "planlanmalıdır; gecikme kayıp riskini artırır.",
     [("amber", "Dane nemini ölç (hedef: %14–16 hasat için)"),
      ("amber", "Hasat zamanlamasını hava durumuna göre planla"),
      ("green", "Kurutma ve depolama kapasitesini hazırla"),
      ("green", "Hasat sonrası toprak analizi planla (sonraki sezon)")]),
]

# Ekim öncesi → ilk aşama (Çimlenme) "başlangıç" olarak işaretlenir
START_IDX = 0

if "bbch_sel" not in st.session_state:
    st.session_state.bbch_sel = START_IDX

st.markdown(section_head("Fenolojik Büyüme Takvimi — BBCH Skalası (Referans)"), unsafe_allow_html=True)

cols = st.columns(len(BBCH_STAGES))
for i, (code, name, short, *_) in enumerate(BBCH_STAGES):
    if i == START_IDX:
        dot_cls = "bbch-dot bbch-dot-start"
        lbl_cls = "bbch-label bbch-label-start"
    else:
        dot_cls = "bbch-dot bbch-dot-future"
        lbl_cls = "bbch-label bbch-label-future"

    if i == st.session_state.bbch_sel:
        dot_cls += " bbch-dot-selected"

    with cols[i]:
        st.markdown(
            f'<div class="bbch-stage" style="padding-bottom:4px">'
            f'  <div class="{dot_cls}">{code}</div>'
            f'  <div class="{lbl_cls}" style="margin-bottom:6px">{short}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("Seç", key=f"bbch_{i}", use_container_width=True,
                     help=f"BBCH {code} — {name} aşamasını görüntüle"):
            st.session_state.bbch_sel = i
            st.rerun()

# ── Seçili aşama detay paneli ──
sel = st.session_state.bbch_sel
s_code, s_name, s_short, s_desc, s_tasks = BBCH_STAGES[sel]

tasks_html = ""
for prio, task in s_tasks:
    tasks_html += (
        f'<div class="bbch-task-item">'
        f'  <div class="bbch-task-dot bbch-task-dot-{prio}"></div>'
        f'  <div>{task}</div>'
        f'</div>'
    )

badge_color = {"green": "var(--ag-accent)", "amber": "var(--ag-amber)", "red": "var(--ag-red)"}
prio_set = {p for p, _ in s_tasks}
urgency = "red" if "red" in prio_set else ("amber" if "amber" in prio_set else "green")

st.markdown(
    f'<div class="bbch-detail">'
    f'  <div class="bbch-detail-code">BBCH {s_code}{"  ·  SONRAKİ AŞAMA" if sel == START_IDX else ""}</div>'
    f'  <div class="bbch-detail-title" style="color:{badge_color[urgency]}">{s_name}</div>'
    f'  <div class="bbch-detail-body">{s_desc}</div>'
    f'  <div class="bbch-detail-tasks">'
    f'    <div class="bbch-detail-tasks-head">Bu Dönemde Yapılacaklar</div>'
    f'    {tasks_html}'
    f'  </div>'
    f'</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="ag-hint">Bir aşamaya tıklayarak o dönemin görevlerini ve detaylarını görüntüleyebilirsin.</div>',
            unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# PDF ÖNİZLEME
# ════════════════════════════════════════════════════════
st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
st.markdown(section_head("Proje Dokümanı — Ulusan AgroTech Solutions 2026"), unsafe_allow_html=True)

if not pdf_pages:
    st.markdown('<div style="opacity:0.5;font-size:13px">ulusan-agrotech-solutions.pdf bu dizinde bulunamadı.</div>',
                unsafe_allow_html=True)
else:
    total = len(pdf_pages)
    idx   = st.session_state["pdf_idx"]

    nav1, nav2, nav3 = st.columns([1, 5, 1])
    with nav1:
        prev = st.button("← Önceki", use_container_width=True, key="pdf_prev")
    with nav3:
        nxt  = st.button("Sonraki →", use_container_width=True, key="pdf_next")
    with nav2:
        st.markdown(
            f'<div style="text-align:center;font-size:12px;opacity:0.5;padding-top:9px">'
            f'Sayfa {idx + 1} / {total}</div>',
            unsafe_allow_html=True,
        )

    if prev and idx > 0:
        st.session_state["pdf_idx"] = idx - 1
        st.rerun()
    if nxt and idx < total - 1:
        st.session_state["pdf_idx"] = idx + 1
        st.rerun()

    _, img_col, _ = st.columns([1, 4, 1])
    with img_col:
        st.markdown(
            f'<div class="pdf-wrap">'
            f'<img src="data:image/png;base64,{pdf_pages[idx]}" alt="Sayfa {idx + 1}">'
            f'</div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════
# ALT BİLGİ
# ════════════════════════════════════════════════════════
st.markdown(
    '<div style="border-top:1px solid var(--ag-line);margin-top:40px;padding-top:14px;'
    'display:flex;justify-content:space-between;font-size:11px;opacity:0.4">'
    '  <span>tarla-ai v0.1.0 &nbsp;·&nbsp; Ekim öncesi referans paneli</span>'
    '  <span>Referans değerler literatür/TAGEM kaynaklıdır — saha verisiyle kalibre edilmesi önerilir</span>'
    '</div>',
    unsafe_allow_html=True,
)
