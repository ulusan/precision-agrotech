"""Saf HTML yardımcıları — Streamlit unsafe_allow_html için."""

from __future__ import annotations


def section_head(label: str) -> str:
    return f'<div class="ag-head">{label}</div>'


def sidebar_head(label: str) -> str:
    return f'<div class="sb-head">{label}</div>'


def cap(text: str) -> str:
    return f'<div class="ag-cap">{text}</div>'


def fmt(v: float) -> str:
    return f"{v:g}"


def tip(text: str, label: str, wide: bool = False) -> str:  # noqa: ARG001 (wide unused — kept for caller compat)
    """Üzerine gelinince açıklama gösteren tooltip span (JS fixed-position sürücüsü)."""
    safe = text.replace('"', "&quot;").replace("'", "&#39;")
    return f'<span class="has-tip" data-tip="{safe}">{label}</span>'


def th(label: str, tip_text: str, width: str = "") -> str:
    """Tooltip'li tablo başlığı <th> elementi."""
    w = f"style='width:{width}'" if width else ""
    safe = tip_text.replace('"', "&quot;").replace("'", "&#39;")
    return (
        f"<th {w}><span class='has-tip' data-tip=\"{safe}\">"
        f"{label}</span></th>"
    )


def n_pill(seviye: str) -> str:
    """Azot ihtiyaç düzeyini renkli pill badge olarak döndürür."""
    s = seviye.lower()
    if "pik" in s or "yüksek" in s:
        cls = "stage-pill-high"
    elif "orta" in s:
        cls = "stage-pill-mid"
    else:
        cls = "stage-pill-low"
    return f'<span class="stage-pill {cls}">{seviye}</span>'
