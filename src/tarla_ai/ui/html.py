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


def tip_attr(text: str) -> str:
    """Tooltip metnini attribute içine gömülebilir hale getirir."""
    return (
        text.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def tip(text: str, label: str, wide: bool = False) -> str:
    """Üzerine gelinince açıklama gösteren tooltip span.

    Saf CSS tooltip kullanır (`data-tip` + `.has-tip:hover::after`) — JS
    gerektirmez (Streamlit st.markdown içindeki <script>'i sterilize eder),
    anında açılır ve gecikme yoktur. `data-tip` attribute'u Streamlit
    sanitizer'dan geçer (doğrulandı).

    Args:
        text: Tooltip içeriği (sade dil açıklaması).
        label: Görünen etiket.
        wide: True ise daha geniş tooltip kutusu (.has-tip-wide).
    """
    cls = "has-tip has-tip-wide" if wide else "has-tip"
    return f'<span class="{cls}" data-tip="{tip_attr(text)}">{label}</span>'


def th(label: str, tip_text: str, width: str = "") -> str:
    """Tooltip'li tablo başlığı <th> elementi (saf CSS `data-tip`)."""
    w = f"style='width:{width}'" if width else ""
    return (
        f"<th {w}><span class='has-tip' data-tip=\"{tip_attr(tip_text)}\">"
        f"{label}</span></th>"
    )


def explainer_body(body: str, legend: tuple[tuple[str, str], ...] = ()) -> str:
    """"Bu nedir?" açıklamasının gövde + renk lejantı HTML'i (başlıksız).

    Başlık + açılır-kapanır sarmal UI katmanındadır (st.expander). Burası
    yalnızca içeriği üretir; saf HTML, Streamlit'e bağımsız (test edilebilir).

    Args:
        body: Sade dilli açıklama; <b> ile vurgu yapılabilir.
        legend: Opsiyonel renk lejantı — (renk_css, etiket) çiftleri.
                Örn. (("var(--ag-accent)", "sorun yok"), ...).
    """
    legend_html = ""
    if legend:
        items = "".join(
            f'<span><span class="explainer-dot" style="background:{color}"></span>'
            f'{label}</span>'
            for color, label in legend
        )
        legend_html = f'<div class="explainer-legend">{items}</div>'
    return (
        f'<div class="explainer-body">{body}</div>'
        f'{legend_html}'
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
