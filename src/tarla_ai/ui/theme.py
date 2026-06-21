"""Dashboard CSS stili ve JS tooltip sürücüsü."""

from __future__ import annotations

DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&display=swap');

:root {
  --ag-accent:  #5db82a;
  --ag-amber:   #c8a84b;
  --ag-red:     #d95030;
  --ag-line:    rgba(255,255,255,0.08);
  --ag-line-2:  rgba(255,255,255,0.12);
  --ag-fill:    rgba(255,255,255,0.04);
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

/* ── Sekmeler (st.tabs) — domain ayrımı ── */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  border-bottom: 1px solid var(--ag-line);
  margin-bottom: 28px;
}
.stTabs [data-baseweb="tab"] {
  height: auto;
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: 6px 6px 0 0;
  font-size: 14px; font-weight: 500;
  color: rgba(232,232,232,0.5);
  transition: color 0.15s, background 0.15s;
}
.stTabs [data-baseweb="tab"]:hover {
  color: rgba(232,232,232,0.85);
  background: var(--ag-fill);
}
.stTabs [aria-selected="true"] {
  color: var(--ag-accent) !important;
  background: rgba(93,184,42,0.07);
}
/* Streamlit'in alt-çizgi vurgusu yeşil olsun */
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { background-color: var(--ag-accent) !important; }

/* ── Durum bandı ── */
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

/* ── "Bu nedir?" açıklama kutusu (st.expander accordion) ── */
[data-testid="stExpander"] details {
  background: var(--ag-fill);
  border: 1px solid var(--ag-line-2);
  border-left: 3px solid var(--ag-accent);
  border-radius: 4px; margin-bottom: 20px;
}
[data-testid="stExpander"] summary {
  font-size: 13px; font-weight: 600;
}
[data-testid="stExpander"] summary:hover { color: var(--ag-accent); }
.explainer-body { font-size: 13px; line-height: 1.7; opacity: 0.82; }
.explainer-body b { opacity: 1; font-weight: 600; }
.explainer-legend {
  margin-top: 12px; padding-top: 12px;
  border-top: 1px dashed var(--ag-line-2);
  display: flex; flex-wrap: wrap; gap: 16px;
  font-size: 12px; opacity: 0.75;
}
.explainer-legend span { display: inline-flex; align-items: center; gap: 6px; }
.explainer-dot {
  width: 9px; height: 9px; border-radius: 50%; display: inline-block;
}
.ref-unit { font-size: 11px; opacity: 0.5; font-weight: 400; }
.ref-unit .has-tip { opacity: 1; }

/* ── Büyüme dönemi tablosu ── */
.stage-pill {
  display: inline-block; font-size: 10px; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase;
  padding: 2px 9px; border-radius: 3px;
}
.stage-pill-low    { border: 1px solid var(--ag-line-2); color: rgba(232,232,232,0.6); }
.stage-pill-mid    { border: 1px solid var(--ag-amber); color: var(--ag-amber); }
.stage-pill-high   { border: 1px solid var(--ag-red); color: var(--ag-red); }

/* ── Tooltip — saf CSS (JS yok, anında, Streamlit-safe) ── */
/* Streamlit st.markdown içindeki <script>'i sterilize ettiği için JS sürücüsü
   çalışmıyordu; native `title` ise gecikmeli/güvenilmezdi. Bu yüzden saf CSS:
   data-tip içeriği :hover'da ::after ile gösterilir. Anında açılır, şık kutu.
   data-tip attribute'unun Streamlit sanitizer'dan geçtiği doğrulandı. */
.has-tip {
  cursor: help;
  border-bottom: 1px dashed rgba(128,128,128,0.45);
  position: relative;
}
.has-tip::after {
  content: attr(data-tip);
  position: absolute;
  bottom: calc(100% + 9px);
  left: 50%;
  transform: translateX(-50%);
  width: max-content; max-width: 280px;
  background: rgba(20,20,20,0.98);
  border: 1px solid var(--ag-line-2);
  border-radius: 6px;
  padding: 10px 13px;
  font-size: 12.5px; font-weight: 400; line-height: 1.6;
  letter-spacing: 0; text-transform: none; text-align: left;
  color: #ededed;
  white-space: normal;
  box-shadow: 0 8px 24px rgba(0,0,0,0.45);
  backdrop-filter: blur(8px);
  opacity: 0; visibility: hidden;
  transition: opacity 0.12s ease, visibility 0.12s;
  z-index: 9999;
  pointer-events: none;
}
/* küçük ok (kutunun altında) */
.has-tip::before {
  content: "";
  position: absolute;
  bottom: calc(100% + 3px);
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: rgba(20,20,20,0.98);
  opacity: 0; visibility: hidden;
  transition: opacity 0.12s ease, visibility 0.12s;
  z-index: 9999;
  pointer-events: none;
}
.has-tip:hover::after,
.has-tip:hover::before { opacity: 1; visibility: visible; }
.has-tip-wide::after { max-width: 360px; }
/* Tablo başlık hücrelerinde tooltip sola hizalı kalsın (kenarda taşmasın) */
.ref-table th:first-child .has-tip::after { left: 0; transform: none; }
.ref-table th:first-child .has-tip::before { left: 16px; transform: none; }

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
"""
