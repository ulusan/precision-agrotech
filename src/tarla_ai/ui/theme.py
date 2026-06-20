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

/* ── Tooltip (fixed-position JS sürücüsü) ── */
.has-tip { cursor: help; border-bottom: 1px dashed rgba(128,128,128,0.4); }
#ag-tooltip {
  display: none; position: fixed; z-index: 99999;
  max-width: 300px;
  background: var(--ag-tip-bg);
  border: 1px solid var(--ag-line-2);
  padding: 11px 14px;
  font-size: 12.5px; color: #e8e8e8; line-height: 1.6;
  font-weight: 400; letter-spacing: 0; text-transform: none;
  backdrop-filter: blur(12px);
  pointer-events: none;
}

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

TOOLTIP_JS = """
<div id="ag-tooltip"></div>
<script>
(function(){
  const box = document.getElementById('ag-tooltip');
  if (!box) return;
  document.addEventListener('mouseover', e => {
    const el = e.target.closest('.has-tip');
    if (!el) return;
    box.textContent = el.getAttribute('data-tip');
    box.style.display = 'block';
  });
  document.addEventListener('mouseout', e => {
    if (!e.target.closest('.has-tip')) return;
    box.style.display = 'none';
  });
  document.addEventListener('mousemove', e => {
    if (box.style.display === 'none') return;
    const bw = box.offsetWidth, vw = window.innerWidth;
    let x = e.clientX + 14;
    if (x + bw > vw - 12) x = e.clientX - bw - 14;
    box.style.left = x + 'px';
    box.style.top  = (e.clientY + 18) + 'px';
  });
})();
</script>
"""
