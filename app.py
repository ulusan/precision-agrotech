"""Pilot Tarla Dashboard — tarla_ai kütüphanesini doğrudan çağırır.

Çalıştır:  uv run streamlit run app.py
"""

from __future__ import annotations

import base64
from pathlib import Path

import fitz  # pymupdf
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from tarla_ai.indices import cwsi, dual_confirmed_stress, vari
from tarla_ai.rules import evaluate_ndre, evaluate_soil_ph
from tarla_ai.rules.engine import Severity

# ── Sayfa yapılandırması ─────────────────────────────────
st.set_page_config(
    page_title="Tarla Raporu — Ulusan AgroTech",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════
# STİL — config.toml tema renklerini MİRAS ALIR.
# Zemin/metin renkleri config.toml'dan gelir (tek doğruluk
# kaynağı); burada SADECE kendi bileşenlerimizi (kart, tablo,
# BBCH, tooltip) ve birkaç token tanımlarız. Streamlit
# widget'larına (slider, buton) DOKUNMAYIZ — onları tema
# motoru doğru renklendirir.
# ════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&display=swap');

/* ══ TASARIM TOKEN'LARI ══ */
:root {
  --ag-accent:  #5db82a;   /* vurgu yeşili (primaryColor ile aynı) */
  --ag-amber:   #c8a84b;
  --ag-red:     #d95030;
  --ag-line:    rgba(255,255,255,0.08);   /* ayırıcı çizgi */
  --ag-line-2:  rgba(255,255,255,0.12);   /* kart kenarı */
  --ag-fill:    rgba(255,255,255,0.04);   /* kart zemini (koyu temada) */
  --ag-tip-bg:  rgba(15,15,15,0.96);      /* tooltip zemini */
}

/* ══ FONT — sadece aile. ÖNEMLİ: Material Symbols ikon
   font'unu (sidebar aç/kapa okları vb.) EZME, yoksa ikon
   yerine ham metin "keyboard_double_arrow_left" çıkar. ══ */
html, body,
.stApp p, .stApp span, .stApp label, .stApp li,
.stApp td, .stApp th, .stApp h1, .stApp h2, .stApp h3,
.stApp button, .stApp input, .stApp a,
[class*="ag-"], [class*="mc-"], [class*="sb-"],
[class*="rec-"], [class*="bbch-"], [class*="soil-"], .has-tip, .tip {
  font-family: 'Space Grotesk', system-ui, sans-serif;
}
/* Material ikon font'u her zaman korunsun */
[class*="material-symbols"],
.material-symbols-rounded,
[data-testid] span[translate="no"] {
  font-family: 'Material Symbols Rounded' !important;
}

/* ══ Deploy butonu + hamburger menü — görünür bırak ══ */

/* ══ SIDEBAR AÇ/KAPA BUTONU — her zaman görünür ══ */
/* Streamlit bu butonları ve içlerini opacity:0 başlatıp
   hover'da 1 yapıyor; tüm alt elementleri de kapsamak
   için * ile force ediyoruz. */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] *,
[data-testid="stExpandSidebarButton"],
[data-testid="stExpandSidebarButton"] * {
  opacity: 1 !important;
  visibility: visible !important;
}

/* ══ Ayırıcı çizgi (st.divider) — token ile ══ */
[data-testid="stDivider"] hr {
  border-color: var(--ag-line) !important;
  margin: 12px 0 !important;
}

/* ══ KENDİ BİLEŞENLERİMİZ ══ */

/* ── Sidebar section başlığı ── */
.sb-head {
  font-size: 9px; font-weight: 600; letter-spacing: 0.14em;
  text-transform: uppercase; opacity: 0.5; margin-bottom: 8px;
}

/* ── Ana içerik section başlığı ── */
.ag-head {
  font-size: 10px; font-weight: 600; letter-spacing: 0.16em;
  text-transform: uppercase; opacity: 0.55;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--ag-line);
  margin-bottom: 18px;
}

/* ── Hint ve caption ── */
.ag-hint { font-size: 11px; opacity: 0.45; margin-top: 10px; margin-bottom: 28px; }
.ag-cap  { font-size: 11px; opacity: 0.5; line-height: 1.5; margin-top: 6px; }

/* ── Kart ── */
.ag-card {
  background: var(--ag-fill);
  border: 1px solid var(--ag-line-2);
  padding: 18px 20px;
}

/* ── Metrik kart bileşenleri ── */
.mc-lbl {
  font-size: 10px; font-weight: 600; letter-spacing: 0.13em;
  text-transform: uppercase; opacity: 0.6; margin-bottom: 0;
}
.mc-val {
  font-size: 28px; font-weight: 600; letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums; line-height: 1;
}
.mc-sub { font-size: 12px; opacity: 0.55; margin-top: 7px; line-height: 1.4; }

/* ── Tablo ── */
.soil-table { width: 100%; border-collapse: collapse; }
.soil-table th {
  font-size: 10px; font-weight: 600; letter-spacing: 0.12em;
  text-transform: uppercase; opacity: 0.5;
  padding: 6px 10px;
  border-bottom: 1px solid var(--ag-line);
  text-align: left;
}
.soil-table td {
  padding: 10px 10px;
  border-bottom: 1px solid var(--ag-line);
  vertical-align: middle; font-size: 13.5px;
}
.soil-table tr:last-child td { border-bottom: none; }
.soil-table td.val {
  font-variant-numeric: tabular-nums; font-weight: 600;
  text-align: right; font-size: 15px;
}
.val-ok   { color: var(--ag-accent); }
.val-warn { color: var(--ag-amber); }

/* ── Öneri satırı ── */
.rec-row {
  display: grid;
  grid-template-columns: 4px 1fr auto;
  gap: 14px; align-items: start;
  padding: 14px 0;
  border-bottom: 1px solid var(--ag-line);
}
.rec-row:last-child { border-bottom: none; }
.rec-bar { width: 4px; min-height: 44px; }
.rec-msg { font-size: 13.5px; line-height: 1.6; }
.rec-val {
  font-size: 22px; font-weight: 600; letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums;
  white-space: nowrap; text-align: right; padding-top: 2px;
}
.rec-lbl {
  font-size: 10px; font-weight: 600; letter-spacing: 0.13em;
  text-transform: uppercase; opacity: 0.7; margin-bottom: 5px;
}

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
.bbch-dot-past     { background: rgba(128,128,128,0.12); border-color: rgba(128,128,128,0.3); }
.bbch-dot-active   { background: var(--ag-accent); border-color: var(--ag-accent); color: #06200a; box-shadow: 0 0 0 4px rgba(93,184,42,0.2); }
.bbch-dot-future   { background: rgba(128,128,128,0.06); border-color: rgba(128,128,128,0.15); opacity: 0.4; }
.bbch-dot-selected { outline: 2px solid #e8e8e8; outline-offset: 3px; }
.bbch-label {
  font-size: 10px; font-weight: 600; letter-spacing: 0.04em;
  margin-top: 9px; text-align: center; line-height: 1.3; padding: 0 4px;
}
.bbch-label-past   { opacity: 0.5; }
.bbch-label-active { color: var(--ag-accent) !important; opacity: 1; }
.bbch-label-future { opacity: 0.3; }

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
.bbch-detail-title {
  font-size: 18px; font-weight: 600; margin-bottom: 14px;
}
.bbch-detail-body {
  font-size: 13px; line-height: 1.7; opacity: 0.85;
}
.bbch-detail-tasks {
  margin-top: 16px; padding-top: 14px;
  border-top: 1px solid var(--ag-line);
}
.bbch-detail-tasks-head {
  font-size: 10px; font-weight: 700; letter-spacing: 0.14em;
  text-transform: uppercase; opacity: 0.45; margin-bottom: 10px;
}
.bbch-task-item {
  display: flex; align-items: flex-start; gap: 10px;
  margin-bottom: 8px; font-size: 13px;
}
.bbch-task-dot {
  width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
  margin-top: 6px;
}
.bbch-task-dot-green  { background: var(--ag-accent); }
.bbch-task-dot-amber  { background: var(--ag-amber); }
.bbch-task-dot-red    { background: var(--ag-red); }

/* ── BBCH "Seç" buton stilini sıfırla — sadece ince bir çizgi ── */
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

# ── Vurgu renkleri (verinin anlamını taşıyan sabitler) ───
C_GREEN  = "#5db82a"   # iyi / normal — config primaryColor ile aynı
C_AMBER  = "#c8a84b"   # uyarı
C_RED    = "#d95030"   # aksiyon / stres
C_MAP_BG = "#0a0a0a"   # matplotlib figür zemini — config backgroundColor ile aynı

SEV_COLOR = {
    Severity.OK:      C_GREEN,
    Severity.WARNING: C_AMBER,
    Severity.ACTION:  C_RED,
}

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

# PDF sayfa durumu — slider key'i KULLANMIYORUZ, sadece buton
if "pdf_idx" not in st.session_state:
    st.session_state["pdf_idx"] = 0  # 0-tabanlı


# ════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div style="font-size:15px;font-weight:600;margin-bottom:2px">Tarla Raporu</div>'
        '<div style="font-size:11px;opacity:0.55;margin-bottom:16px">Ulusan AgroTech Solutions</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown(sidebar_head("Termal Kamera Referansları"), unsafe_allow_html=True)
    t_wet = st.slider("Serin yaprak sıcaklığı (°C)", 10.0, 25.0, 18.5, 0.5,
        help="Su stresi hesabında alt referans. Aynı uçuşta en serin, sağlıklı bitkinin yaprak sıcaklığı.")
    t_dry = st.slider("Stresli yaprak sıcaklığı (°C)", 25.0, 45.0, 32.0, 0.5,
        help="Su stresi hesabında üst referans. Aynı uçuşta susuz, stresli bitkinin yaprak sıcaklığı.")
    st.divider()

    st.markdown(sidebar_head("Analiz Eşikleri"), unsafe_allow_html=True)
    cwsi_thresh  = st.slider("Su stresi eşiği", 0.1, 0.9, 0.50, 0.05,
        help="Bu değerin üzerindeki alanlar su stresli kabul edilir. 0 = stres yok, 1 = ciddi stres.")
    vigor_thresh = st.slider("Düşük canlılık eşiği", 0.0, 0.5, 0.10, 0.05,
        help="Bu değerin altındaki alanlar zayıf bitki örtüsü olarak işaretlenir.")
    ndre_thresh  = st.slider("Azot eksikliği eşiği", 0.1, 0.5, 0.20, 0.01, format="%.2f",
        help="Bu değerin altında gübre uygulaması önerilir. Literatür referansı: 0.20.")
    st.divider()

    st.markdown(sidebar_head("Toprak Değerleri"), unsafe_allow_html=True)
    soil_ph  = st.slider("pH", 4.0, 9.0, 6.8, 0.1,
        help="Toprağın asitlik-bazlık dengesi. Buğday/arpa için ideal aralık 6.0–7.5.")
    soil_om  = st.slider("Organik Madde (%)", 0.5, 5.0, 1.9, 0.1,
        help="Topraktaki organik madde oranı. 2.5% altı uzun vadeli verim için risk oluşturur.")
    ndre_val = st.slider("NDRE değeri", 0.05, 0.60, 0.147, 0.001, format="%.3f",
        help="Drone veya uydudan ölçülen, parselin azot durumunu gösteren spektral indeks değeri.")
    st.divider()
    st.markdown('<div style="font-size:11px;opacity:0.45">Tarla: 48 ha · BBCH 32 · Sapa Kalkma</div>',
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# SENTETİK TARLA VERİSİ
# ════════════════════════════════════════════════════════
@st.cache_data
def build_synthetic_field(seed: int = 42) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    SIZE = 64
    XX, YY = np.meshgrid(np.linspace(0, 1, SIZE), np.linspace(0, 1, SIZE))
    base = (0.4 * np.sin(XX * np.pi * 1.2) * np.sin(YY * np.pi * 0.9)
            + 0.25 * rng.uniform(-1, 1, (SIZE, SIZE))).astype(np.float32)
    dist    = np.sqrt((XX - 0.25) ** 2 + (YY - 0.77) ** 2)
    hotspot = np.clip(1 - dist / 0.22, 0, 1).astype(np.float32)
    canopy_raw  = base + 0.8 * hotspot
    lo, hi      = canopy_raw.min(), canopy_raw.max()
    canopy_norm = (canopy_raw - lo) / (hi - lo)
    vigor_raw   = (0.35 * np.sin(XX * np.pi * 1.5) * np.sin(YY * np.pi * 1.1)
                   + 0.2 * rng.uniform(-1, 1, (SIZE, SIZE)) - 0.6 * hotspot).astype(np.float32)
    lo2, hi2    = vigor_raw.min(), vigor_raw.max()
    vigor_norm  = (vigor_raw - lo2) / (hi2 - lo2)
    return {"canopy_norm": canopy_norm, "vigor_norm": vigor_norm}


field       = build_synthetic_field()
canopy_c    = (field["canopy_norm"] * (t_dry - t_wet) + t_wet).astype(np.float32)
cwsi_map    = cwsi(canopy_c, t_wet=t_wet, t_dry=t_dry)
vari_map    = (field["vigor_norm"] * 0.5 - 0.05).astype(np.float32)
stress_mask = dual_confirmed_stress(cwsi_map, vari_map,
                                    cwsi_threshold=cwsi_thresh,
                                    vigor_threshold=vigor_thresh)
stress_pct  = float(stress_mask.mean() * 100)
cwsi_mean   = float(cwsi_map.mean())
vari_mean   = float(vari_map.mean())
rec_azot    = evaluate_ndre(ndre_val, threshold=ndre_thresh)
rec_ph      = evaluate_soil_ph(soil_ph)


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
    '      Pilot Tarla &mdash; Canlı Alan Raporu</div>'
    '    <div style="font-size:13px;opacity:0.55;margin-top:8px">'
    '      DJI Mavic 3 Enterprise &nbsp;&middot;&nbsp; RGB + Termal LWIR + RTK'
    '      &nbsp;&middot;&nbsp; Sentinel-2 multispektral &nbsp;&middot;&nbsp; Buğday &amp; Arpa'
    '    </div>'
    '  </div>'
    '  <div style="text-align:right;font-size:12px;opacity:0.6;line-height:2">'
    '    <div style="font-size:16px;font-weight:600;opacity:1;letter-spacing:-0.01em">'
    '      <span class="has-tip" style="border-bottom:1px dashed rgba(128,128,128,0.5)">'
    '        BBCH 32'
    '        <span class="tip" style="right:0;left:auto;transform:none;width:260px">'
    '          BBCH (Biologische Bundesanstalt, Bundessortenamt und CHemische Industrie) bitkinin büyüme '
    '          evresini tanımlayan uluslararası standart skalasıdır.<br><br>'
    '          <b>BBCH 32 — Sapa Kalkma, 2. Boğum:</b> Bitki toprak yüzeyinden ikinci boğumunu '
    '          yukarı itmektedir. Bu evre azot ihtiyacının en yoğun olduğu dönemdir; '
    '          su ve besin eksiklikleri tane oluşumunu kalıcı olarak etkiler.'
    '        </span>'
    '      </span>'
    '      &nbsp;&mdash;&nbsp; Sapa Kalkma</div>'
    '    19 Haziran 2026 &nbsp;&middot;&nbsp; 48 ha'
    '  </div>'
    '</div>',
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════
# BBCH FENOLOJİK AŞAMA DİYAGRAMI
# ════════════════════════════════════════════════════════
# Her aşama: (kod, ad, açıklama, kısa_etiket, görevler)
# Görevler: (öncelik, metin)  öncelik: "green" | "amber" | "red"
BBCH_STAGES = [
    ("00", "Çimlenme", "Ekim — Çimlenme",
     "Tohum toprağa verilir; su alımıyla şişme ve çimlenme başlar. "
     "Toprak nemi homojen olmalı, ekim derinliği 3–5 cm idealdir.",
     [("green", "Tohum yatağı hazırlığını kontrol et"),
      ("green", "Ekim derinliğini 3–5 cm ayarla"),
      ("amber", "Çimlenme sıcaklığını izle (min 4 °C)"),
      ("amber", "Toprak nem sensörü verilerini kontrol et")]),

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
     "aşırı azot bu aşamada aşırı kardeşlenmeye neden olabilir.",
     [("green", "Kardeş sayısını say (hedef: 3–5 kardeş/bitki)"),
      ("green", "İlk azot dozunu uygula (30–40 kg N/ha)"),
      ("amber", "Herbisit uygulaması için uygun pencereyi belirle"),
      ("amber", "Kışlık ekimde don zararını kontrol et")]),

    ("30", "Sapa Kalkma", "Sapa Kalkma",
     "Bitki boyunu hızla artırır; boğumlar birbirinden uzaklaşır. "
     "Azot ve su ihtiyacı bu evrede en yüksek noktadadır. "
     "Yatma riski bu aşamada değerlendirilir.",
     [("green", "İkinci azot dozunu uygula (40–60 kg N/ha)"),
      ("green", "Fungisit ihtiyacını değerlendir"),
      ("amber", "Yatma riskine karşı büyüme düzenleyici uygula"),
      ("red",   "Su stresini izle — kritik verim penceresi")]),

    ("32", "Boğum 2 — Şimdi", "Boğum 2 ★ Şimdi",
     "İkinci boğum toprak yüzeyinden en az 2 cm yukarıdadır. "
     "Kritik pencere: bu noktada yapılacak azot uygulaması tane "
     "protein içeriğini doğrudan etkiler. Termal görüntüleme ile "
     "su stresi tespiti bu aşamada en doğru sonucu verir.",
     [("red",   "Azot uygulaması — protein kalitesi için kritik pencere"),
      ("red",   "Su stresini CWSI ile izle (eşik: 0.50)"),
      ("amber", "NDRE ile azot durumunu kontrol et"),
      ("green", "Hastalık baskısını (pas, septoria) değerlendir")]),

    ("51", "Başak Çıkışı", "Başak Çıkışı",
     "Başak yaprak kılıfından çıkmaya başlar (salkım ucu görünür). "
     "Bu evre hastalık baskısının arttığı dönemdir; "
     "özellikle sarı pas ve septoria dikkatle izlenmelidir.",
     [("red",   "Fungisit uygulaması — sarı pas ve septoria"),
      ("amber", "Başak gelişimini ve homojenliği izle"),
      ("green", "Yaprak alan indeksini değerlendir"),
      ("amber", "Dolu ve aşırı yağış riskini takip et")]),

    ("65", "Tam Çiçeklenme", "Çiçeklenme",
     "Başağın %50'sinden fazlasında çiçeklenme tamamlanmıştır. "
     "Fungisit uygulaması için kritik pencere; dane bağlama başlar. "
     "Fusarium riski bu aşamada maksimuma ulaşır.",
     [("red",   "Fusarium'a karşı fungisit uygula — en kritik pencere"),
      ("red",   "Sıcaklık + nem kombinasyonunu izle (fusarium riski)"),
      ("amber", "Sulama programını dane doldurma için ayarla"),
      ("green", "Çiçeklenme homojenliğini kaydet")]),

    ("71", "Süt Olum", "Süt Olum",
     "Daneler dolmaya başlar; içeriği sütümsü kıvamda, yeşil renkte. "
     "Su ve sıcaklık stresi bu evrede dane ağırlığını düşürür. "
     "Son sulama fırsatı bu aşamaya kadardır.",
     [("amber", "Son sulama kararını ver (toprak nem eşiği %40)"),
      ("amber", "Dane dolum hızını izle"),
      ("green", "Kuş ve zararlı baskısını kontrol et"),
      ("green", "Hasat ekipmanı bakımını planla")]),

    ("87", "Sarı Olum", "Sarı Olum",
     "Daneler sarılaşmış, nem %35'in altına inmiştir. "
     "Erken hasat makinelere zarar verebilir. "
     "Hava durumu takibi ve hasat lojistiği planlanmalıdır.",
     [("amber", "Dane nemini ölç (hedef: %14–16 hasat için)"),
      ("amber", "Hasat zamanlamasını hava durumuna göre planla"),
      ("green", "Kurutma ve depolama kapasitesini hazırla"),
      ("green", "Hasat kayıplarını minimize etmek için ayar yap")]),

    ("99", "Hasat", "Hasat",
     "Dane nemi %14 civarı; biçer-döver için ideal olgunluk. "
     "Gecikmeli hasat çatlama ve kayıp riskini artırır. "
     "Hasat sonrası toprak analizi bir sonraki sezon için planlanır.",
     [("red",   "Hasatı geciktirme — nem artışı ve kayıp riski"),
      ("amber", "Hasat kaybı oranını kaydet"),
      ("green", "Toprak analizi yaptır (bir sonraki sezon için)"),
      ("green", "Anız yönetimi planla (toprak organik maddesi)")]),
]

ACTIVE_IDX = next(i for i, s in enumerate(BBCH_STAGES) if s[0] == "32")

if "bbch_sel" not in st.session_state:
    st.session_state.bbch_sel = ACTIVE_IDX

# ── Zaman çizelgesi butonları ──
st.markdown(section_head("Fenolojik Büyüme Takvimi — BBCH Skalası"), unsafe_allow_html=True)

cols = st.columns(len(BBCH_STAGES))
for i, (code, name, short, *_) in enumerate(BBCH_STAGES):
    is_active   = i == ACTIVE_IDX
    is_selected = i == st.session_state.bbch_sel

    if i < ACTIVE_IDX:
        dot_cls = "bbch-dot bbch-dot-past"
        lbl_cls = "bbch-label bbch-label-past"
    elif i == ACTIVE_IDX:
        dot_cls = "bbch-dot bbch-dot-active"
        lbl_cls = "bbch-label bbch-label-active"
    else:
        dot_cls = "bbch-dot bbch-dot-future"
        lbl_cls = "bbch-label bbch-label-future"

    if is_selected:
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
prio_counts = {}
for prio, _ in s_tasks:
    prio_counts[prio] = prio_counts.get(prio, 0) + 1
urgency = "red" if "red" in prio_counts else ("amber" if "amber" in prio_counts else "green")

st.markdown(
    f'<div class="bbch-detail">'
    f'  <div class="bbch-detail-code">BBCH {s_code}{"  ·  ŞU AN" if sel == ACTIVE_IDX else ""}</div>'
    f'  <div class="bbch-detail-title" style="color:{badge_color[urgency]}">{s_name}</div>'
    f'  <div class="bbch-detail-body">{s_desc}</div>'
    f'  <div class="bbch-detail-tasks">'
    f'    <div class="bbch-detail-tasks-head">Bu Dönemde Yapılacaklar</div>'
    f'    {tasks_html}'
    f'  </div>'
    f'</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="ag-hint">Bir aşamaya tıklayarak o dönemin görevlerini ve detaylarını görüntüleyebilirsin.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# METRİK KARTLAR
# ════════════════════════════════════════════════════════
def metric_card(label: str, tip: str, value: str, sub: str, accent: str) -> str:
    return (
        f'<div class="ag-card">'
        f'  <div class="has-tip" style="margin-bottom:8px">'
        f'    <div class="mc-lbl">{label}</div>'
        f'    <span class="tip">{tip}</span>'
        f'  </div>'
        f'  <div class="mc-val" style="color:{accent}">{value}</div>'
        f'  <div class="mc-sub">{sub}</div>'
        f'</div>'
    )

m1, m2, m3, m4 = st.columns(4)
m1.markdown(metric_card(
    "Su Stresi İndeksi",
    "Bitkinin ne kadar susuz kaldığını gösteren ısıl ölçüm. "
    "0 = hiç stres yok, 1 = ciddi stres. Termal kamera ile ölçülür.",
    f"{cwsi_mean:.3f}",
    f"Eşik: {cwsi_thresh:.2f} — {'stres eşiği aşıldı' if cwsi_mean > cwsi_thresh else 'normal aralık'}",
    C_RED if cwsi_mean > cwsi_thresh else C_GREEN,
), unsafe_allow_html=True)

m2.markdown(metric_card(
    "Bitki Canlılığı",
    "Bitkinin yeşillik ve canlılık düzeyi. Yüksek değer sağlıklı bitki örtüsü, "
    "düşük değer seyrek veya stresli bitki demektir. RGB fotoğraftan hesaplanır.",
    f"{vari_mean:.3f}",
    f"Düşük canlılık sınırı: VARI &lt; {vigor_thresh:.2f}",
    C_GREEN,
), unsafe_allow_html=True)

m3.markdown(metric_card(
    "Öncelikli Müdahale Alanı",
    "Hem su stresi hem düşük bitki canlılığının birlikte gözlemlendiği, "
    "ilk müdahale gerektiren alan yüzdesi.",
    f"%{stress_pct:.1f}",
    "Değişken doz uygulaması için öncelikli bölge",
    C_RED if stress_pct > 20 else C_AMBER,
), unsafe_allow_html=True)

m4.markdown(metric_card(
    "Azot Durumu",
    "Bitkinin azot içeriğini gösteren kızılötesi spektral ölçüm. "
    "Düşük değer yaprak sarılığı ve verim kaybına yol açar; gübre takviyesi gerektirir.",
    f"{ndre_val:.3f}",
    f"Eşik: {ndre_thresh:.2f} — {'gübre önerilir' if ndre_val < ndre_thresh else 'yeterli'}",
    C_RED if ndre_val < ndre_thresh else C_GREEN,
), unsafe_allow_html=True)

st.markdown("<div style='margin-top:32px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# HARİTALAR
# ════════════════════════════════════════════════════════
st.markdown(section_head("Uzaktan Algılama Haritaları"), unsafe_allow_html=True)

cwsi_cmap   = mcolors.LinearSegmentedColormap.from_list("cwsi",   [(0,"#0f3020"),(0.5,C_AMBER),(1,C_RED)])
vari_cmap   = mcolors.LinearSegmentedColormap.from_list("vari",   [(0,"#1a2e1a"),(0.5,"#3a6020"),(1,C_GREEN)])
stress_cmap = mcolors.LinearSegmentedColormap.from_list("stress", [(0,"#1a2e1a"),(1,C_RED)])

def render_map(ax: plt.Axes, data: np.ndarray, cmap: mcolors.Colormap,
               title: str, vmin: float = 0.0, vmax: float = 1.0) -> None:
    ax.set_facecolor(C_MAP_BG)
    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax,
                   interpolation="bilinear", aspect="equal")
    ax.set_title(title, color="#e8e8e8", fontsize=9, fontweight="600", pad=6, loc="left")
    ax.axis("off")
    cb = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, format="%.2f")
    cb.ax.tick_params(colors="#999999", labelsize=7)
    cb.outline.set_edgecolor("#333333")

map_col1, map_col2, map_col3 = st.columns(3)

with map_col1:
    fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor=C_MAP_BG)
    render_map(ax, cwsi_map, cwsi_cmap, "Su Stresi Dağılımı")
    ax.contour(cwsi_map, levels=[cwsi_thresh], colors=[C_RED], linewidths=0.8, alpha=0.6)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown(cap(f"Kırmızı kontur stres sınırını gösterir (CWSI = {cwsi_thresh:.2f}) · DJI LWIR termal kamera"),
                unsafe_allow_html=True)

with map_col2:
    fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor=C_MAP_BG)
    render_map(ax, vari_map, vari_cmap, "Bitki Canlılığı", vmin=-0.1, vmax=0.5)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown(cap(f"Koyu alanlar zayıf bitki örtüsünü gösterir (VARI &lt; {vigor_thresh:.2f}) · DJI RGB ortomosaik"),
                unsafe_allow_html=True)

with map_col3:
    fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor=C_MAP_BG)
    render_map(ax, stress_mask.astype(np.float32), stress_cmap,
               f"Öncelikli Müdahale Bölgesi — %{stress_pct:.0f}")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown(cap("Her iki eşiği birden aşan alanlar · Değişken doz uygulaması için öncelik bölgesi"),
                unsafe_allow_html=True)

st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# ÖNERİLER + TOPRAK TABLOSU
# ════════════════════════════════════════════════════════
rec_col, soil_col = st.columns([3, 2])

with rec_col:
    st.markdown(section_head("Sistem Önerileri"), unsafe_allow_html=True)

    def rec_row_html(label: str, message: str, value: str, accent: str) -> str:
        return (
            f'<div class="rec-row">'
            f'  <div class="rec-bar" style="background:{accent}"></div>'
            f'  <div>'
            f'    <div class="rec-lbl" style="color:{accent}">{label}</div>'
            f'    <div class="rec-msg">{message}</div>'
            f'  </div>'
            f'  <div class="rec-val" style="color:{accent}">{value}</div>'
            f'</div>'
        )

    st.markdown(rec_row_html(
        "Azot Durumu", rec_azot.message,
        f"{rec_azot.value:.3f}", SEV_COLOR[rec_azot.severity],
    ), unsafe_allow_html=True)

    st.markdown(rec_row_html(
        "Toprak Asitliği", rec_ph.message,
        f"{rec_ph.value:.1f}", SEV_COLOR[rec_ph.severity],
    ), unsafe_allow_html=True)

    ws_accent = C_RED if cwsi_mean > cwsi_thresh else C_GREEN
    ws_msg = (
        f"Parsel ortalaması {cwsi_mean:.3f} — stres sınırını ({cwsi_thresh:.2f}) aştı. "
        f"Güneybatı köşesinde %{stress_pct:.0f} alan öncelikli sulama gerektiriyor."
        if cwsi_mean > cwsi_thresh else
        f"Parsel ortalaması {cwsi_mean:.3f} — stres sınırının altında. Sulama normal seyrediyor."
    )
    st.markdown(rec_row_html("Su Stresi", ws_msg, f"{cwsi_mean:.3f}", ws_accent),
                unsafe_allow_html=True)


with soil_col:
    st.markdown(section_head("Toprak Analizi — Temel Panel"), unsafe_allow_html=True)

    soil_rows: list[tuple[str, float, str, float, float, str]] = [
        ("pH", soil_ph, "", 6.0, 7.5,
         "Toprağın asitlik-bazlık ölçüsü. 0–14 arası bir sayıdır; 7 nötrdür. "
         "Buğday ve arpa için 6.0–7.5 idealdir. Bu aralığın dışında besin maddeleri bitkiye ulaşamaz."),
        ("Organik Madde", soil_om, "%", 2.5, 99.0,
         "Topraktaki çürümüş bitki ve hayvan kalıntılarının oranı. Suyu ve besin maddelerini tutar, "
         "toprak yapısını iyileştirir. 2.5% altı uzun vadede verim düşüşüne yol açar."),
        ("Toplam Azot", 0.12, "%", 0.10, 99.0,
         "Toprağın organik ve mineral azot içeriği. Azot bitkinin en fazla tükettiği besindir; "
         "yaprak ve sap gelişimini doğrudan etkiler."),
        ("Fosfor", 48.0, "kg/ha", 20.0, 99.0,
         "Bitkiye yarayışlı fosfor miktarı. Kök gelişimini ve çiçeklenmeyi destekler. "
         "Kg/ha: bir hektar alandaki kilogram miktarı."),
        ("Potasyum", 186.0, "kg/ha", 80.0, 99.0,
         "Bitkinin su dengesini, hastalık direncini ve tane ağırlığını etkileyen temel besin. "
         "Sapa kalkma döneminde bitki potasyum talebi en yüksektir."),
        ("Tuzluluk", 0.34, "dS/m", 0.0, 0.8,
         "Topraktaki çözünmüş tuzların yoğunluğu. Yüksek tuzluluk bitkinin kökten su almasını engeller. "
         "0.8 dS/m altı buğday ve arpa için güvenlidir."),
        ("Çinko", 0.6, "mg/kg", 1.0, 99.0,
         "Protein sentezi ve enzim üretimi için gerekli iz element. 1 mg/kg altında eksiklik "
         "başak gelişimini ve verimi düşürür. Yüksek pH çinkonun bitkiye geçişini engeller."),
        ("Katyon Değişim Kap.", 22.0, "meq/100g", 10.0, 99.0,
         "Toprağın besin maddesi tutma kapasitesi. Yüksek değer, gübre kayıplarının az olduğu "
         "anlamına gelir. 10 meq/100g üzeri yeterli kabul edilir."),
    ]

    rows_html = ""
    for name, val, unit, lo, hi, tip in soil_rows:
        ok         = lo <= val <= hi
        val_cls    = "val-ok" if ok else "val-warn"
        pill_color = C_GREEN if ok else C_AMBER
        pill_txt   = "Normal" if ok else "Dikkat"
        val_str    = f"{val:.2f}".rstrip("0").rstrip(".")
        rows_html += (
            f"<tr>"
            f"  <td><span class='has-tip'>{name}"
            f"    <span class='tip'>{tip}</span></span></td>"
            f"  <td class='val {val_cls}'>{val_str}"
            f"    <span style='font-size:10px;font-weight:400;opacity:0.5'> {unit}</span></td>"
            f"  <td style='text-align:right'>"
            f"    <span style='display:inline-block;font-size:10px;font-weight:600;"
            f"    letter-spacing:0.10em;text-transform:uppercase;padding:2px 8px;"
            f"    border:1px solid {pill_color};color:{pill_color}'>{pill_txt}</span></td>"
            f"</tr>"
        )

    st.markdown(
        "<table class='soil-table'>"
        "  <thead><tr>"
        "    <th>Parametre</th>"
        "    <th style='text-align:right'>Değer</th>"
        "    <th style='text-align:right'>Durum</th>"
        "  </tr></thead>"
        f"  <tbody>{rows_html}</tbody>"
        "</table>",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════
# PDF ÖNİZLEME
# ════════════════════════════════════════════════════════
st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)
st.markdown(section_head("Proje Dokümanı — Ulusan AgroTech Solutions 2026"), unsafe_allow_html=True)

if not pdf_pages:
    st.markdown('<div style="opacity:0.5;font-size:13px">ulusan-agrotech-solutions.pdf bu dizinde bulunamadı.</div>',
                unsafe_allow_html=True)
else:
    total = len(pdf_pages)
    idx   = st.session_state["pdf_idx"]  # 0-tabanlı

    # Butonlar — session_state'i BUTON callback'inde değiştir
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

    # Güncelleme: buton tıklandıktan SONRA, widget'lar çizildi; değişkeni güncelle + rerun
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
    '  <span>tarla-ai v0.1.0 &nbsp;·&nbsp; Faz 0–1 &nbsp;·&nbsp; Kural tabanlı karar motoru</span>'
    '  <span>Eşik değerleri literatür referansına dayalıdır — saha verisiyle kalibre edilmesi önerilir</span>'
    '</div>',
    unsafe_allow_html=True,
)
