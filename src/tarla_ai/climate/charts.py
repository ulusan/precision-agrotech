"""Sezon iklim grafikleri — saf SVG üretir (JS yok, kendi içinde tam).

Hem standalone HTML rapor hem Streamlit arayüzü bu fonksiyonları kullanır;
çıktı doğrudan <svg> markup'ıdır, st.markdown(unsafe_allow_html=True) ile
veya bir HTML dosyasına gömülerek render edilebilir.
"""

from __future__ import annotations

from datetime import date

from tarla_ai.climate.analysis import (
    cumulative_gdd,
    cumulative_rain,
    monthly_breakdown,
)
from tarla_ai.climate.models import DailyWeather

# Palet (uygulama kimliği ile uyumlu somut hex'ler)
C_INK    = "#e9ebe9"
C_ACCENT = "#5db82a"
C_WATER  = "#5da0d0"
C_AMBER  = "#c8a84b"
C_RED    = "#d95030"
C_SNOW   = "#9fb8c8"
C_GRID   = "rgba(255,255,255,0.06)"
C_MUTED  = "rgba(233,235,233,0.55)"

_AY_KISA = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz",
            "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]

W, H = 1000, 300
PADL, PADR, PADT, PADB = 54, 18, 22, 42


def _x(i: int, n: int) -> float:
    return PADL if n <= 1 else PADL + (W - PADL - PADR) * i / (n - 1)


def _y(v: float, vmax: float, vmin: float = 0.0) -> float:
    if vmax <= vmin:
        return H - PADB
    return (H - PADB) - (H - PADB - PADT) * (v - vmin) / (vmax - vmin)


def _month_ticks(dates: list[date]) -> list[tuple[int, str]]:
    ticks, seen = [], set()
    for i, dt in enumerate(dates):
        key = (dt.year, dt.month)
        if key not in seen:
            seen.add(key)
            ticks.append((i, _AY_KISA[dt.month]))
    return ticks


def _xlabels(dates: list[date]) -> str:
    out, n = [], len(dates)
    for i, lbl in _month_ticks(dates):
        x = _x(i, n)
        out.append(f'<line x1="{x:.1f}" y1="{PADT}" x2="{x:.1f}" y2="{H-PADB}" '
                   f'stroke="{C_GRID}" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{H-PADB+20}" text-anchor="middle" '
                   f'fill="{C_MUTED}" font-size="11">{lbl}</text>')
    return "".join(out)


def _hgrid(vmax: float, vmin: float, steps: int = 4, suffix: str = "") -> str:
    out = []
    for k in range(steps + 1):
        val = vmin + (vmax - vmin) * k / steps
        y = _y(val, vmax, vmin)
        out.append(f'<line x1="{PADL}" y1="{y:.1f}" x2="{W-PADR}" y2="{y:.1f}" '
                   f'stroke="{C_GRID}" stroke-width="1"/>')
        out.append(f'<text x="{PADL-8}" y="{y+3:.1f}" text-anchor="end" '
                   f'fill="{C_MUTED}" font-size="11">{val:.0f}{suffix}</text>')
    return "".join(out)


def _today_marker(dates: list[date], today: date) -> str:
    n = len(dates)
    for i, dt in enumerate(dates):
        if dt > today:
            x = _x(i, n)
            return (f'<line x1="{x:.1f}" y1="{PADT}" x2="{x:.1f}" y2="{H-PADB}" '
                    f'stroke="{C_MUTED}" stroke-width="1" stroke-dasharray="3,3"/>'
                    f'<text x="{x-4:.1f}" y="{PADT+11}" text-anchor="end" '
                    f'fill="{C_MUTED}" font-size="10">bugün</text>'
                    f'<text x="{x+4:.1f}" y="{PADT+11}" text-anchor="start" '
                    f'fill="{C_MUTED}" font-size="10">tahmin →</text>')
    return ""


def _svg(inner: str) -> str:
    return (f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" '
            f'style="width:100%;height:auto;display:block">{inner}</svg>')


def _area_line(series: list[tuple[date, float, bool]], color: str, unit: str,
               today: date, fill_op: float = 0.14) -> str:
    dates = [r[0] for r in series]
    vals = [r[1] for r in series]
    n = len(vals)
    vmax = max(vals) * 1.08 if vals and max(vals) > 0 else 1.0
    pts = [(_x(i, n), _y(v, vmax)) for i, v in enumerate(vals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = (f"M{pts[0][0]:.1f},{H-PADB} "
            + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts)
            + f" L{pts[-1][0]:.1f},{H-PADB} Z")
    last_i = max((i for i, r in enumerate(series) if not r[2]), default=n - 1)
    ex, ey = pts[last_i]
    gid = "g" + color.replace("#", "").replace("(", "").replace(")", "").replace(",", "")[:8]
    inner = (
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{color}" stop-opacity="{fill_op}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
        + _hgrid(vmax, 0) + _xlabels(dates)
        + f'<path d="{area}" fill="url(#{gid})"/>'
        + f'<polyline points="{line}" fill="none" stroke="{color}" '
          f'stroke-width="2.4" stroke-linejoin="round"/>'
        + _today_marker(dates, today)
        + f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.5" fill="{color}"/>'
        + f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="9" fill="{color}" opacity="0.22"/>'
        + f'<text x="{ex-10:.1f}" y="{ey-12:.1f}" text-anchor="end" fill="{C_INK}" '
          f'font-size="14" font-weight="600">{vals[last_i]:.0f} {unit}</text>'
    )
    return _svg(inner)


def cumulative_rain_svg(days: list[DailyWeather], today: date | None = None) -> str:
    """Ekim'den bugüne kümülatif yağış — alan dolgulu çizgi."""
    today = today or date.today()
    return _area_line(cumulative_rain(days), C_WATER, "mm", today)


def gdd_svg(days: list[DailyWeather], today: date | None = None) -> str:
    """Kümülatif GDD (büyüme gün dereceleri) — yeşil çizgi."""
    today = today or date.today()
    return _area_line(cumulative_gdd(days), C_ACCENT, "°C·gün", today)


def monthly_rain_svg(days: list[DailyWeather], today: date | None = None) -> str:
    """Aylık yağış — yağmur + kar suyu yığılı çubuk."""
    months = monthly_breakdown(days)
    if not months:
        return _svg("")
    n = len(months)
    vmax = max((m.rain_mm + m.snow_water_mm) for m in months) * 1.15
    vmax = max(vmax, 10.0)
    bw = (W - PADL - PADR) / n * 0.6
    parts = []
    for k in range(5):
        val = vmax * k / 4
        y = H - PADB - (H - PADB - PADT) * k / 4
        parts.append(f'<line x1="{PADL}" y1="{y:.1f}" x2="{W-PADR}" y2="{y:.1f}" '
                     f'stroke="{C_GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{PADL-8}" y="{y+3:.1f}" text-anchor="end" '
                     f'fill="{C_MUTED}" font-size="11">{val:.0f}</text>')
    for i, m in enumerate(months):
        cx = PADL + (W - PADL - PADR) * (i + 0.5) / n
        x = cx - bw / 2
        yb = H - PADB
        hr = (H - PADB - PADT) * m.rain_mm / vmax
        hs = (H - PADB - PADT) * m.snow_water_mm / vmax
        parts.append(f'<rect x="{x:.1f}" y="{yb-hr:.1f}" width="{bw:.1f}" '
                     f'height="{hr:.1f}" fill="{C_WATER}" rx="2"/>')
        if m.snow_water_mm > 0.3:
            parts.append(f'<rect x="{x:.1f}" y="{yb-hr-hs:.1f}" width="{bw:.1f}" '
                         f'height="{hs:.1f}" fill="{C_SNOW}" rx="2"/>')
        tot = m.rain_mm + m.snow_water_mm
        parts.append(f'<text x="{cx:.1f}" y="{yb-hr-hs-7:.1f}" text-anchor="middle" '
                     f'fill="{C_INK}" font-size="12" font-weight="600">{tot:.0f}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{H-PADB+20}" text-anchor="middle" '
                     f'fill="{C_MUTED}" font-size="11">{_AY_KISA[m.month]}</text>')
    return _svg("".join(parts))


def temp_band_svg(days: list[DailyWeather], today: date | None = None) -> str:
    """Günlük gece–gündüz sıcaklık bandı + 0°C don ve 30°C sıcak çizgileri."""
    today = today or date.today()
    dd = sorted(days, key=lambda x: x.date)
    dates = [d.date for d in dd]
    tmax = [d.temp_max for d in dd]
    tmin = [d.temp_min for d in dd]
    valid = [t for t in tmax + tmin if t is not None]
    if not valid:
        return _svg("")
    vmax, vmin = max(valid) + 4, min(valid) - 3
    n = len(dd)

    def pt(vals: list[float | None]) -> list[tuple[float, float]]:
        return [(_x(i, n), _y(v if v is not None else vmin, vmax, vmin))
                for i, v in enumerate(vals)]

    pmax, pmin = pt(tmax), pt(tmin)
    band = ("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pmax)
            + " L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in reversed(pmin)) + " Z")
    lmax = " ".join(f"{x:.1f},{y:.1f}" for x, y in pmax)
    lmin = " ".join(f"{x:.1f},{y:.1f}" for x, y in pmin)

    grid = []
    lo = int(vmin // 10 * 10)
    hi = int(vmax // 10 * 10 + 10)
    for val in range(lo, hi + 1, 10):
        y = _y(val, vmax, vmin)
        grid.append(f'<line x1="{PADL}" y1="{y:.1f}" x2="{W-PADR}" y2="{y:.1f}" '
                    f'stroke="{C_GRID}" stroke-width="1"/>')
        grid.append(f'<text x="{PADL-8}" y="{y+3:.1f}" text-anchor="end" '
                    f'fill="{C_MUTED}" font-size="11">{val}°</text>')
    y0 = _y(0, vmax, vmin)
    y30 = _y(30, vmax, vmin)
    lines = (
        f'<line x1="{PADL}" y1="{y0:.1f}" x2="{W-PADR}" y2="{y0:.1f}" stroke="{C_WATER}" '
        f'stroke-width="1" stroke-dasharray="4,3"/>'
        f'<text x="{W-PADR}" y="{y0-5:.1f}" text-anchor="end" fill="{C_WATER}" '
        f'font-size="10">0°C don sınırı</text>'
        f'<line x1="{PADL}" y1="{y30:.1f}" x2="{W-PADR}" y2="{y30:.1f}" stroke="{C_RED}" '
        f'stroke-width="1" stroke-dasharray="4,3"/>'
        f'<text x="{W-PADR}" y="{y30-5:.1f}" text-anchor="end" fill="{C_RED}" '
        f'font-size="10">30°C sıcak stresi</text>'
    )
    inner = ("".join(grid) + _xlabels(dates)
             + f'<path d="{band}" fill="{C_AMBER}" opacity="0.13"/>'
             + f'<polyline points="{lmax}" fill="none" stroke="{C_RED}" '
               f'stroke-width="1.6" opacity="0.85"/>'
             + f'<polyline points="{lmin}" fill="none" stroke="{C_WATER}" '
               f'stroke-width="1.6" opacity="0.85"/>'
             + lines + _today_marker(dates, today))
    return _svg(inner)
