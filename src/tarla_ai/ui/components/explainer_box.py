"""Açılır-kapanır "Bu nedir?" açıklama kutusu (accordion).

Yeni başlayan birine sade dille anlatan kutuyu st.expander içinde gösterir;
referans tablolar açık kalırken bu açıklamalar isteğe bağlı açılır/kapanır.

Saf HTML gövdesi html.explainer_body()'den gelir (test edilebilir); buradaki
katman yalnızca Streamlit expander sarmalını ekler.
"""

from __future__ import annotations

import streamlit as st

from tarla_ai.ui.html import explainer_body


def render_explainer(
    title: str,
    body: str,
    icon: str = "💡",
    legend: tuple[tuple[str, str], ...] = (),
    expanded: bool = False,
) -> None:
    """Açılır-kapanır açıklama kutusunu render eder.

    Args:
        title: Başlık (expander etiketi olarak gösterilir).
        body: Sade dilli açıklama; <b> ile vurgu yapılabilir.
        icon: Başlık emojisi (etikette başa eklenir).
        legend: Opsiyonel renk lejantı — (renk_css, etiket) çiftleri.
        expanded: Varsayılan açık mı? (False = kapalı başlar)
    """
    with st.expander(f"{icon}  {title}", expanded=expanded):
        st.markdown(explainer_body(body, legend), unsafe_allow_html=True)
