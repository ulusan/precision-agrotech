"""Hava Durumu & İklim paneli — Open-Meteo verisiyle, konum bazlı, sade Türkçe.

Tüm metinler hiç tarım/hava bilmeyen biri için günlük dille yazılır;
kısaltmalar tooltip'te açıklanır (labels.GLOSSARY). Konum seçilebilir:
varsayılan pilot tarla (Bahçekaradalak), ayrıca Üçem/Karadalak/Boyalık.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from tarla_ai.climate.analysis import analyze_by_stage, monthly_breakdown, season_summary
from tarla_ai.climate.charts import (
    cumulative_rain_svg,
    gdd_svg,
    monthly_rain_svg,
    temp_band_svg,
)
from tarla_ai.climate.client import fetch_season
from tarla_ai.climate.labels import GLOSSARY, weather_text
from tarla_ai.climate.models import DailyWeather, StageWeatherSummary
from tarla_ai.climate.reference import (
    DEFAULT_LOCATION,
    LOCATIONS,
    STAGE_MIN_RAIN_MM,
    Location,
    location_by_key,
)
from tarla_ai.ui.components.explainer_box import render_explainer
from tarla_ai.ui.html import cap, section_head, th

_SEASON_START = date(2025, 10, 1)

# ── Renkler ───────────────────────────────────────────────────────────────────
_OK    = "var(--ag-accent)"
_WARN  = "var(--ag-amber)"
_RED   = "var(--ag-red)"
_MUTED = "var(--ag-line)"
_BLUE  = "#5da0d0"

_GUN_ADI = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


# ── Veri yükleme (konuma göre önbellek) ──────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def _load_climate(lat: float, lon: float) -> list[DailyWeather] | None:
    """Saat başı yenilenen iklim verisi (lat/lon başına ayrı önbellek)."""
    try:
        return fetch_season(lat, lon, _SEASON_START, forecast_days=16)
    except Exception:
        return None


# ── Küçük gösterim yardımcıları ──────────────────────────────────────────────

def _rain_bar(mm: float, max_mm: float = 150.0) -> str:
    pct = min(100, round(mm / max_mm * 100)) if max_mm > 0 else 0
    return (
        f"<div style='display:flex;align-items:center;gap:6px'>"
        f"<div style='width:54px;background:rgba(255,255,255,0.08);border-radius:3px;height:6px'>"
        f"<div style='width:{pct}%;background:{_BLUE};height:6px;border-radius:3px'></div></div>"
        f"<span>{mm:.0f} mm</span></div>"
    )


def _deficit_pill(deficit_mm: float) -> str:
    """Su açığı/fazlası rozeti — sade etiketle."""
    if deficit_mm > 20:
        color, label = _RED, f"{deficit_mm:.0f} mm su açığı"
    elif deficit_mm < -10:
        color, label = _OK, f"{abs(deficit_mm):.0f} mm yağış fazlası"
    else:
        color, label = _WARN, "dengeli"
    return (
        f"<span class='stage-pill' style='border:1px solid {color};color:{color};"
        f"font-size:10px'>{label}</span>"
    )


def _stress_pill(frost: int, heat: int) -> str:
    parts = []
    if frost > 0:
        parts.append(
            f"<span class='stage-pill' style='border:1px solid {_BLUE};color:{_BLUE}'>"
            f"❄ {frost} gün don</span>"
        )
    if heat > 0:
        parts.append(
            f"<span class='stage-pill' style='border:1px solid {_RED};color:{_RED}'>"
            f"🌡 {heat} gün sıcak</span>"
        )
    return " ".join(parts) if parts else "<span style='opacity:0.4'>yok</span>"


def _stage_status(s: StageWeatherSummary) -> tuple[str, str]:
    if not s.has_data:
        return _MUTED, "HENÜZ GELMEDİ"
    min_rain = STAGE_MIN_RAIN_MM.get(s.stage_name, 0)
    if s.water_deficit_mm > 30 or s.total_rain_mm < min_rain * 0.5:
        return _RED, "KURAK"
    if s.water_deficit_mm > 10 or s.total_rain_mm < min_rain * 0.8:
        return _WARN, "SINIRDA"
    return _OK, "YETERLİ"


# ── Konum seçici + künye ──────────────────────────────────────────────────────

def _select_location() -> Location:
    """Mahalle/konum seçici. Varsayılan: pilot tarla."""
    labels = [loc.label for loc in LOCATIONS]
    keys = [loc.key for loc in LOCATIONS]
    idx = st.selectbox(
        "Hangi konumun havası?",
        options=range(len(LOCATIONS)),
        format_func=lambda i: labels[i],
        index=0,
        help="Tüm hava bilgisi seçtiğiniz konuma göre gösterilir. Varsayılan, "
             "tarım kararlarının verildiği pilot tarladır (Bahçekaradalak).",
        key="climate_location",
    )
    return location_by_key(keys[idx])


def _render_location_card(loc: Location) -> None:
    is_pilot = loc.key == DEFAULT_LOCATION.key
    note = loc.note
    if not is_pilot:
        note += (
            " Hava bölgeseldir; bu mahalle ile pilot tarlanın değerleri birbirine "
            "çok yakın çıkar. Tarım kararları için pilot tarla konumu esastır."
        )
    lbl = 'font-size:11px;opacity:0.5;margin-bottom:4px'
    sub = 'font-size:11px;opacity:0.4;margin-top:4px'
    st.markdown(
        f'<div class="ag-card" style="display:grid;'
        f'grid-template-columns:1.4fr 1fr 1fr;gap:18px;margin:6px 0 18px">'
        f'<div><div style="{lbl}">Seçili konum</div>'
        f'<div style="font-size:14px;font-weight:600">{loc.label}</div>'
        f'<div style="font-size:11px;opacity:0.55;margin-top:4px;'
        f'line-height:1.5">{note}</div></div>'
        f'<div><div style="{lbl}">Koordinat</div>'
        f'<div style="font-size:13px;font-weight:600">{loc.lat:.5f}, {loc.lon:.5f}</div>'
        f'<div style="{sub}">enlem, boylam</div></div>'
        f'<div><div style="{lbl}">Veri kaynağı</div>'
        f'<div style="font-size:13px;font-weight:600">Open-Meteo</div>'
        f'<div style="{sub}">ücretsiz · ERA5 + ECMWF</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Bugünkü koşullar (metrik kartlar) ─────────────────────────────────────────

def _render_today_cards(days: list[DailyWeather]) -> None:
    today = date.today()
    today_data = next((d for d in days if d.date == today), None)
    past = [d for d in days if not d.is_forecast]
    ref = today_data or (past[-1] if past else None)
    ref_label = "Bugün" if today_data else (ref.date.strftime("%d.%m") if ref else "—")

    emoji, desc = weather_text(ref.weather_code if ref else None)
    if ref is not None and ref.temp_max is not None and ref.temp_min is not None:
        temp_str = f"{ref.temp_min:.0f}° / {ref.temp_max:.0f}°"
    else:
        temp_str = "—"
    rain_v = ref.precipitation_mm if ref else None
    rain_str = f"{rain_v:.1f} mm" if rain_v is not None else "0.0 mm"
    hum_str  = f"%{ref.humidity_pct:.0f}" if ref and ref.humidity_pct is not None else "—"
    wind_str = f"{ref.wind_max_kmh:.0f} km/sa" if ref and ref.wind_max_kmh is not None else "—"

    last7 = [d for d in days if 0 <= (today - d.date).days <= 7 and not d.is_forecast]
    rain7 = sum(d.precipitation_mm or 0 for d in last7)

    cards = [
        (f"{ref_label} · Hava", f"{emoji} {desc}" if emoji else desc, "genel durum"),
        (f"{ref_label} · Sıcaklık", temp_str, "gece / gündüz"),
        (f"{ref_label} · Yağış", rain_str, "bugün düşen"),
        ("Son 7 Gün · Yağış", f"{rain7:.0f} mm", "toplam"),
        (f"{ref_label} · Nem", hum_str, "havadaki su buharı"),
        (f"{ref_label} · Rüzgâr", wind_str, "en yüksek hız"),
    ]
    cols = st.columns(6)
    for col, (title, value, sub) in zip(cols, cards, strict=False):
        size = "15px" if title.endswith("Hava") else "19px"
        with col:
            st.markdown(
                f'<div class="ag-card" style="text-align:center;min-height:96px">'
                f'<div style="font-size:10px;opacity:0.5;margin-bottom:6px">{title}</div>'
                f'<div style="font-size:{size};font-weight:600;line-height:1.25">{value}</div>'
                f'<div style="font-size:10px;opacity:0.4;margin-top:6px">{sub}</div>'
                f'</div>', unsafe_allow_html=True,
            )


# ── Önümüzdeki günler — okunabilir tahmin şeridi ─────────────────────────────

def _render_forecast_strip(days: list[DailyWeather]) -> None:
    today = date.today()
    forecast = [d for d in days if d.date >= today][:12]
    if not forecast:
        st.markdown("<div style='opacity:0.5;font-size:13px'>Tahmin alınamadı.</div>",
                    unsafe_allow_html=True)
        return

    cards = ""
    for d in forecast:
        emoji, _desc = weather_text(d.weather_code)
        gun = "Bugün" if d.date == today else _GUN_ADI[d.date.weekday()]
        tmax = f"{d.temp_max:.0f}°" if d.temp_max is not None else "—"
        tmin = f"{d.temp_min:.0f}°" if d.temp_min is not None else "—"
        rain = d.precipitation_mm or 0.0
        prob = d.precip_probability
        rain_line = (
            f"<div style='font-size:11px;color:{_BLUE};margin-top:3px'>💧 {rain:.0f} mm</div>"
            if rain >= 0.1 else
            "<div style='font-size:11px;opacity:0.35;margin-top:3px'>kuru</div>"
        )
        prob_line = (
            f"<div style='font-size:10px;opacity:0.5'>%{prob:.0f} ihtimal</div>"
            if prob is not None and rain >= 0.1 else ""
        )
        cards += (
            f"<div style='flex:1;min-width:72px;text-align:center;padding:10px 4px;"
            f"border:1px solid var(--ag-line);border-radius:8px;background:rgba(255,255,255,0.02)'>"
            f"<div style='font-size:11px;opacity:0.6;margin-bottom:4px'>{gun}</div>"
            f"<div style='font-size:11px;opacity:0.4'>{d.date.strftime('%d.%m')}</div>"
            f"<div style='font-size:22px;margin:4px 0'>{emoji}</div>"
            f"<div style='font-size:13px;font-weight:600'>{tmax}</div>"
            f"<div style='font-size:11px;opacity:0.5'>{tmin}</div>"
            f"{rain_line}{prob_line}"
            f"</div>"
        )
    st.markdown(
        f"<div style='display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px'>{cards}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        cap("Üst sıra: gündüz en yüksek, alt: gece en düşük sıcaklık (°C). "
            "💧 o gün beklenen yağış (mm) ve gerçekleşme ihtimali. "
            "'Kuru' = yağış beklenmiyor."),
        unsafe_allow_html=True,
    )


def _render_forecast_charts(days: list[DailyWeather]) -> None:
    today = date.today()
    forecast = [d for d in days if d.date >= today][:16]
    if not forecast:
        return
    df = pd.DataFrame({
        "Tarih":      [d.date.strftime("%d.%m") for d in forecast],
        "Yağış (mm)": [d.precipitation_mm or 0.0 for d in forecast],
        "Gündüz °C":  [d.temp_max or 0.0 for d in forecast],
        "Gece °C":    [d.temp_min or 0.0 for d in forecast],
    }).set_index("Tarih")

    a, b = st.columns(2)
    with a:
        st.markdown('<div style="font-size:12px;opacity:0.6;margin-bottom:4px">'
                    'Günlük beklenen yağış (mm)</div>', unsafe_allow_html=True)
        st.bar_chart(df[["Yağış (mm)"]], height=170, color=_BLUE)
    with b:
        st.markdown('<div style="font-size:12px;opacity:0.6;margin-bottom:4px">'
                    'Gündüz / gece sıcaklık (°C)</div>', unsafe_allow_html=True)
        st.line_chart(df[["Gündüz °C", "Gece °C"]], height=170)


# ── Büyüme dönemi iklim tablosu ───────────────────────────────────────────────

def _render_stage_table(summaries: list[StageWeatherSummary]) -> None:
    rows = ""
    for s in summaries:
        color, label = _stage_status(s)
        status_html = (f"<span class='stage-pill' style='border:1px solid {color};"
                       f"color:{color}'>{label}</span>")
        if s.has_data:
            snow = (f" <span style='opacity:0.5'>+{s.total_snow_cm:.0f}cm kar</span>"
                    if s.total_snow_cm >= 0.5 else "")
            rain_html = _rain_bar(s.total_rain_mm) + snow
            temp_html = f"{s.avg_temp_c:.1f} °C"
            hum_html  = f"%{s.avg_humidity_pct:.0f}"
            et0_html  = f"{s.total_et0_mm:.0f} mm"
            def_html  = _deficit_pill(s.water_deficit_mm)
            stress_html = _stress_pill(s.frost_days, s.heat_days)
            days_html = f"{s.rainy_days} yağışlı / {s.day_count} gün"
        else:
            rain_html = temp_html = hum_html = et0_html = def_html = stress_html = (
                "<span style='opacity:0.3'>—</span>")
            days_html = "<span style='opacity:0.3'>veri yok</span>"

        rows += (
            f"<tr>"
            f"<td><span class='ref-param'>{s.stage_name}</span><br>"
            f"  <span style='font-size:10px;opacity:0.45'>{days_html}</span></td>"
            f"<td class='ref-ideal' style='opacity:0.6'>{s.bbch}</td>"
            f"<td style='font-size:11px;opacity:0.6'>"
            f"  {s.start_date.strftime('%d.%m')}–{s.end_date.strftime('%d.%m.%y')}</td>"
            f"<td>{rain_html}</td>"
            f"<td class='ref-ideal'>{temp_html}</td>"
            f"<td class='ref-ideal'>{hum_html}</td>"
            f"<td class='ref-note'>{et0_html}</td>"
            f"<td>{def_html}</td>"
            f"<td>{stress_html}</td>"
            f"<td>{status_html}</td>"
            f"</tr>"
        )

    st.markdown(
        "<table class='ref-table'><thead><tr>"
        + th("Dönem", "Buğdayın gelişim aşaması ve o döneme düşen yağışlı gün sayısı.", "16%")
        + th("BBCH", GLOSSARY["bbch"], "6%")
        + th("Tarih", "Dönemin başlangıç–bitiş tarihleri.", "12%")
        + th("Yağış", GLOSSARY["yagis"], "13%")
        + th("Ort. Sıcaklık", GLOSSARY["sicaklik"], "9%")
        + th("Nem", GLOSSARY["nem"], "6%")
        + th("Buharlaşma (ET₀)", GLOSSARY["et0"], "8%")
        + th("Su Dengesi", GLOSSARY["su_dengesi"], "12%")
        + th("Stres", GLOSSARY["don"] + " " + GLOSSARY["sicak_stresi"], "11%")
        + th("Durum", "Yağışın yeterli mi yoksa kurak mı olduğunun özeti.", "7%")
        + f"</tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )


# ── Sezon grafikleri (Ekim'den bugüne — SVG) ──────────────────────────────────

def _chart_card(title: str, desc: str, svg: str) -> None:
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;margin-bottom:2px">{title}</div>'
        f'<div style="font-size:11.5px;opacity:0.55;line-height:1.5;margin-bottom:8px">{desc}</div>'
        f'<div class="ag-card" style="padding:14px 14px 8px;overflow-x:auto">{svg}</div>',
        unsafe_allow_html=True,
    )


def _render_season_charts(days: list[DailyWeather]) -> None:
    """Ekim 2025'ten bugüne 4 sezon grafiği: yağış, GDD, aylık yağış, sıcaklık."""
    _chart_card(
        "Kümülatif yağış (mm)",
        "Sezon başından beri toprağa düşen tüm suyun toplamı; sürekli artar. Dik "
        "çıktığı yerde bol yağış, düz gittiği yerde kuraklık. Kesik çizgi bugünü ayırır.",
        cumulative_rain_svg(days),
    )
    st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
    _chart_card(
        "Sıcaklık birikimi — GDD (°C·gün)",
        "Buğdayın gelişmesi için biriken sıcaklığın gün gün toplamı (bitkinin 'ısı "
        "saati'). Ekmeklik buğday hasada kadar kabaca 2000–2300 °C·gün biriktirir.",
        gdd_svg(days),
    )
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
        _chart_card(
            "Aylık yağış (mm)",
            "Her ayın toplam yağışı — koyu mavi yağmur, açık mavi karın su eşdeğeri.",
            monthly_rain_svg(days),
        )
    with col2:
        st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
        _chart_card(
            "Gece–gündüz sıcaklık (°C)",
            "Günlük en düşük (mavi) ve en yüksek (kırmızı) sıcaklık; 0°C don, 30°C sıcak sınırı.",
            temp_band_svg(days),
        )


# ── Verileri doğrulama kaynakları ─────────────────────────────────────────────

def _render_verify_sources(loc: Location, days: list[DailyWeather]) -> None:
    """Gösterilen hava verisini bağımsız kaynaklardan doğrulama rehberi."""
    months = monthly_breakdown(days)
    feb = next((m for m in months if m.month == 2), None)
    feb_txt = (f"Örnek: bu panelde <b>Şubat {feb.year}</b> toplam yağışı "
               f"<b>{feb.rain_mm + feb.snow_water_mm:.0f} mm</b> görünüyor. "
               f"Aşağıdaki ilk linke tıklarsan aynı sayıyı kaynağında (ham veri) görürsün."
               if feb else "")
    api_url = (f"https://archive-api.open-meteo.com/v1/archive?"
               f"latitude={loc.lat:.4f}&longitude={loc.lon:.4f}"
               f"&start_date=2026-02-01&end_date=2026-02-28"
               f"&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"
               f"&timezone=Europe%2FIstanbul")
    with st.expander("🔎  Bu hava verilerini nasıl doğrularım? (ör. Şubat)"):
        st.markdown(
            f"<div style='font-size:13px;line-height:1.7;opacity:0.85'>"
            f"Buradaki hava verisi <b>Open-Meteo</b>'nun ERA5 arşivinden gelir "
            f"(NASA/ECMWF ölçümlerine dayanan, bilimsel bir yeniden-analiz veri seti). "
            f"İstediğin ayı bağımsız kaynaklardan karşılaştırabilirsin. {feb_txt}</div>"
            f"<ul style='font-size:13px;line-height:1.8;margin-top:10px'>"
            f"<li><b>Open-Meteo (aynı kaynak, ham veri)</b> — seçili konumun "
            f"({loc.lat:.4f}, {loc.lon:.4f}) Şubat verisi: "
            f"<a href='{api_url}' target='_blank'>arşiv API linki</a>. "
            f"Sayfada <code>precipitation_sum</code> değerlerini topla.</li>"
            f"<li><b>MGM — Meteoroloji Genel Müdürlüğü</b> (resmî, Ankara istasyonu): "
            f"<a href='https://www.mgm.gov.tr/veridegerlendirme/il-ve-ilceler-istatistik.aspx' "
            f"target='_blank'>mgm.gov.tr istatistik</a>.</li>"
            f"<li><b>NASA POWER</b> (bağımsız, koordinat bazlı tarım verisi): "
            f"<a href='https://power.larc.nasa.gov/data-access-viewer/' target='_blank'>"
            f"power.larc.nasa.gov</a> — enlem/boylam gir, günlük yağış/sıcaklık al.</li>"
            f"<li><b>Time and Date</b> (kullanımı kolay, Ankara geçmiş hava): "
            f"<a href='https://www.timeanddate.com/weather/turkey/ankara/historic' "
            f"target='_blank'>timeanddate.com</a>.</li>"
            f"</ul>"
            f"<div style='font-size:12px;opacity:0.6;margin-top:6px'>Not: İstasyon "
            f"bazlı kaynaklar (MGM) ile noktasal model verisi (Open-Meteo) arasında "
            f"küçük farklar normaldir; eğilim ve aylık toplamlar tutmalıdır.</div>",
            unsafe_allow_html=True,
        )


# ── Ana render ────────────────────────────────────────────────────────────────

def render_climate_panel() -> None:
    """Hava Durumu sekmesinin tüm içeriğini render eder."""

    st.markdown(section_head("Hava Durumu & İklim Kaydı — Bala / Ankara · 2025–2026 Sezonu"),
                unsafe_allow_html=True)

    render_explainer(
        "Bu panel ne işe yarar? (önce bunu okuyun)",
        "Buğday tarlasının başarısını en çok belirleyen şey <b>havadır</b>: "
        "ne kadar <b>yağmur/kar</b> düştü, hava <b>ne kadar sıcak/soğuk</b>, "
        "<b>nem</b> ve <b>rüzgâr</b> ne durumda. Bu panel, tarlanızın bulunduğu "
        "yerin havasını <b>Open-Meteo</b> adlı ücretsiz kaynaktan otomatik çeker "
        "(para veya şifre gerekmez) ve buğdayın her gelişim döneminde havanın "
        "uygun olup olmadığını söyler.<br><br>"
        "<b>Üç bölüm var:</b> "
        "<b>(1)</b> bugünün havası ve önümüzdeki ~2 haftanın günlük tahmini; "
        "<b>(2)</b> buğdayın her döneminde (çimlenme, kardeşlenme, sapa kalkma…) "
        "ne kadar yağış düştüğü, kaç gün don/sıcak olduğu ve toprağın susuz kalıp "
        "kalmadığı; <b>(3)</b> sezon başından bugüne toplam yağış grafiği.<br><br>"
        "Tablolardaki <b>renkli etiketler</b> durumu özetler. Kısaltmaların "
        "(ET₀, BBCH, nem…) üstüne <b>fareyle gelirseniz</b> ne olduğu sade dille açılır. "
        "Gelecek dönemler için tahmin uydurulmaz; '<b>henüz gelmedi</b>' yazar.",
        icon="🌤️",
        legend=(
            (_OK,   "yeterli — yağış yeterli, su sıkıntısı yok"),
            (_WARN, "sınırda — dikkat etmek gerek"),
            (_RED,  "kurak — toprak susuz, sulama düşünülmeli"),
            (_MUTED, "henüz gelmedi — o dönem yaşanmadı"),
        ),
        expanded=False,
    )

    # ── Konum seçimi ──────────────────────────────────────────────
    loc = _select_location()
    _render_location_card(loc)

    with st.spinner(f"{loc.label} için hava verisi yükleniyor (Open-Meteo)…"):
        days = _load_climate(loc.lat, loc.lon)

    if days is None:
        st.warning("⚠️ Open-Meteo'ya şu an ulaşılamadı. İnternet bağlantısını kontrol "
                   "edip birkaç dakika sonra tekrar deneyin.", icon="🌐")
        return
    if not days:
        st.info("Bu konum için henüz iklim verisi yok.", icon="ℹ️")
        return

    st.markdown(
        '<div style="font-size:12px;font-weight:600;opacity:0.7;letter-spacing:0.04em;'
        'margin:4px 0 14px">📅 Bu panel son 12 ayın <b>gerçek hava kaydını</b> ve '
        '16 günlük tahmini gösterir — tarla henüz ekilmediği için bir referanstır. '
        'Veriler Open-Meteo\'dan otomatik gelir.</div>',
        unsafe_allow_html=True,
    )

    # ── 1) Bugün + tahmin ─────────────────────────────────────────
    _render_today_cards(days)

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
    st.markdown(section_head("Önümüzdeki Günler — Günlük Hava Tahmini"),
                unsafe_allow_html=True)
    _render_forecast_strip(days)
    st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
    _render_forecast_charts(days)

    # ── 2) Büyüme dönemi tablosu ──────────────────────────────────
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    st.markdown(section_head("Buğdayın Her Döneminde Hava — Yağış, Nem, Sıcaklık ve Stres"),
                unsafe_allow_html=True)
    render_explainer(
        "Bu tablo neden önemli?",
        "Buğdayın su ve sıcaklık ihtiyacı her dönemde farklıdır. Örneğin "
        "<b>sapa kalkma</b> ve <b>çiçeklenme</b> dönemlerinde su çok kritiktir; "
        "bu dönemde kuraklık olursa verim ciddi düşer. Tablo, her dönemde gerçekte "
        "ne kadar yağış düştüğünü ve toprağın susuz kalıp kalmadığını gösterir; "
        "böylece hangi dönemde sulama gerektiğini önceden görebilirsiniz.",
        icon="🌱",
    )
    summaries = analyze_by_stage(days)
    _render_stage_table(summaries)

    total_rain = sum(s.total_rain_mm for s in summaries if s.has_data)
    total_et0  = sum(s.total_et0_mm for s in summaries if s.has_data)
    done = sum(1 for s in summaries if s.has_data)
    net = total_et0 - total_rain
    net_txt = (f"toprak {net:.0f} mm su açığında (kurak eğilim)" if net > 0
               else f"{abs(net):.0f} mm yağış fazlası (nemli)")
    st.markdown(
        cap(f"Yaşanan dönem: {done}/{len(summaries)} · "
            f"Sezon toplam yağış: {total_rain:.0f} mm · "
            f"Toplam buharlaşma (ET₀): {total_et0:.0f} mm · "
            f"Genel su dengesi: {net_txt}. "
            f"Geçmiş veriler Open-Meteo ERA5 ölçüm arşivinden, tahmin ECMWF modelinden."),
        unsafe_allow_html=True,
    )

    # ── 3) Sezon grafikleri (Ekim'den bugüne) ─────────────────────
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    st.markdown(section_head("Sezon Grafikleri — Ekim 2025'ten Bugüne"),
                unsafe_allow_html=True)
    summ = season_summary(days)
    st.markdown(
        cap(f"Sezon özeti: {summ.total_rain_mm:.0f} mm yağış · {summ.rainy_days} yağışlı gün · "
            f"GDD {summ.total_gdd:.0f} · {summ.frost_days} don günü · "
            f"{summ.heat_days} sıcak gün · {summ.vernalization_days} soğuklama günü."),
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    _render_season_charts(days)

    # ── Verileri doğrula ──────────────────────────────────────────
    _render_verify_sources(loc, days)

    # ── Kısaltma sözlüğü ──────────────────────────────────────────
    st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
    with st.expander("📖  Kısaltmalar ve terimler — hepsi sade dille"):
        terms = [
            ("Yağış (mm)", GLOSSARY["yagis"]),
            ("Yağmur / Kar", GLOSSARY["yagmur"] + " " + GLOSSARY["kar"]),
            ("Sıcaklık (gece/gündüz)", GLOSSARY["sicaklik"]),
            ("Nem (%)", GLOSSARY["nem"]),
            ("Rüzgâr (km/sa)", GLOSSARY["ruzgar"]),
            ("ET₀ — Buharlaşma", GLOSSARY["et0"]),
            ("Su Dengesi", GLOSSARY["su_dengesi"]),
            ("Don", GLOSSARY["don"]),
            ("Sıcak stresi", GLOSSARY["sicak_stresi"]),
            ("BBCH", GLOSSARY["bbch"]),
            ("Yağışlı gün", GLOSSARY["yagisli_gun"]),
        ]
        body = "".join(
            f'<div style="margin-bottom:10px"><b>{name}</b><br>'
            f'<span style="font-size:13px;opacity:0.75;line-height:1.55">{desc}</span></div>'
            for name, desc in terms
        )
        st.markdown(body, unsafe_allow_html=True)
