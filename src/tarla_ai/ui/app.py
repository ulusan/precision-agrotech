"""Dashboard orkestratörü — sayfa yapılandırması + bileşen akışı."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from tarla_ai.ui.components.bbch_calendar import render_bbch_calendar
from tarla_ai.ui.components.growth_table import render_growth_table, render_nitrogen_card
from tarla_ai.ui.components.soil_table import render_soil_table
from tarla_ai.ui.components.uploaded_data import render_uploaded_drone, render_uploaded_soil
from tarla_ai.ui.html import cap, section_head, sidebar_head
from tarla_ai.ui.pdf_view import render_pdf_panel
from tarla_ai.ui.theme import DASHBOARD_CSS, TOOLTIP_JS

_PDF_PATH = Path(__file__).parents[3] / "ulusan-agrotech-solutions.pdf"


def run() -> None:
    st.set_page_config(
        page_title="Tarla Referans Paneli — Ulusan AgroTech",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.markdown(TOOLTIP_JS, unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────
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
            'Toprak analizi PDF\'i ve drone GeoTIFF\'i buradan yükle. '
            'Yüklenen değerler aşağıda referans aralıklarıyla karşılaştırılır. '
            'Veri yoksa panel referans modunda kalır.'
            '</div>',
            unsafe_allow_html=True,
        )
        soil_file = st.file_uploader(
            "Toprak analiz raporu (PDF)",
            type=["pdf"],
            help="Metin katmanlı (taranmış değil) lab raporu PDF'i.",
            key="soil_pdf_upload",
        )
        drone_file = st.file_uploader(
            "Drone görüntüsü (GeoTIFF)",
            type=["tif", "tiff"],
            help="RGB (3 bant) veya termal (tek bant, °C) georeferanslı GeoTIFF.",
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

    # ── Başlık ────────────────────────────────────────────────
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

    # ── Durum bandı — yalnızca hiç veri yüklenmemişse göster ──
    if soil_file is None and drone_file is None:
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

    # ── Yüklenen gerçek veri (varsa) ──────────────────────────
    if soil_file is not None:
        render_uploaded_soil(soil_file.getvalue())
        st.markdown("<div style='margin-top:36px'></div>", unsafe_allow_html=True)
    if drone_file is not None:
        render_uploaded_drone(drone_file.getvalue())
        st.markdown("<div style='margin-top:36px'></div>", unsafe_allow_html=True)

    # ── Tablo 1: Toprak besin referans aralıkları ─────────────
    st.markdown(
        section_head("Toprak Besin Referans Aralıkları — Buğday (Ankara/Bala Kıraç)"),
        unsafe_allow_html=True,
    )
    render_soil_table()

    st.markdown("<div style='margin-top:36px'></div>", unsafe_allow_html=True)

    # ── Tablo 2: Büyüme dönemine göre N/su ───────────────────
    st.markdown(
        section_head("Büyüme Dönemine Göre Azot ve Su İhtiyacı — Kıraç Buğday"),
        unsafe_allow_html=True,
    )
    render_growth_table()
    render_nitrogen_card()

    st.markdown("<div style='margin-top:36px'></div>", unsafe_allow_html=True)

    # ── BBCH takvimi ──────────────────────────────────────────
    st.markdown(
        section_head("Fenolojik Büyüme Takvimi — BBCH Skalası (Referans)"),
        unsafe_allow_html=True,
    )
    render_bbch_calendar()

    # ── PDF önizleme ──────────────────────────────────────────
    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        section_head("Proje Dokümanı — Ulusan AgroTech Solutions 2026"),
        unsafe_allow_html=True,
    )
    render_pdf_panel(_PDF_PATH)

    # ── Alt bilgi ─────────────────────────────────────────────
    st.markdown(
        '<div style="border-top:1px solid var(--ag-line);margin-top:40px;padding-top:14px;'
        'display:flex;justify-content:space-between;font-size:11px;opacity:0.4">'
        '  <span>tarla-ai v0.1.0 &nbsp;·&nbsp; Ekim öncesi referans paneli</span>'
        '  <span>Referans değerler literatür/TAGEM kaynaklıdır — saha verisiyle kalibre edilmesi önerilir</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(cap(""), unsafe_allow_html=True)
