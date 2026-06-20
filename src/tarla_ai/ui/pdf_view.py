"""PDF önizleme bileşeni — fitz (pymupdf) izole burada."""

from __future__ import annotations

import base64
from pathlib import Path

import fitz  # pymupdf
import streamlit as st


@st.cache_data
def load_pdf_pages(pdf_path: str, dpi_scale: float = 1.6) -> list[str]:
    """PDF'nin her sayfasını base64 PNG string listesi olarak döndürür."""
    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(dpi_scale, dpi_scale)
    pages: list[str] = []
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pages.append(base64.b64encode(pix.tobytes("png")).decode())
    doc.close()
    return pages


def render_pdf_panel(pdf_path: Path) -> None:
    """Sayfa ileri/geri navigasyonlu PDF görüntüleme paneli."""
    if not pdf_path.exists():
        st.markdown(
            '<div style="opacity:0.5;font-size:13px">PDF bu dizinde bulunamadı.</div>',
            unsafe_allow_html=True,
        )
        return

    pdf_pages = load_pdf_pages(str(pdf_path))
    total = len(pdf_pages)

    if "pdf_idx" not in st.session_state:
        st.session_state["pdf_idx"] = 0

    idx = st.session_state["pdf_idx"]

    nav1, nav2, nav3 = st.columns([1, 5, 1])
    with nav1:
        prev = st.button("← Önceki", use_container_width=True, key="pdf_prev")
    with nav3:
        nxt = st.button("Sonraki →", use_container_width=True, key="pdf_next")
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
