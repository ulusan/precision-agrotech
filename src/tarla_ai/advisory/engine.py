"""Öneri motoru — bugünden ileriye, EKİM ÖNCESİNDEN başlayan serüven.

Her aşamada DÖRT veri kaynağının (su / toprak / drone / hava) o aşamada TOPRAĞA
ve BİTKİYE ne yapılacağına nasıl katkı verdiği ayrı ayrı üretilir:
  - Hava: Open-Meteo (gerçek, her zaman bağlı).
  - Su:   pilot tarlanın gerçek kuyu analizi (WELL_WATER_BASELINE, EC 2.90).
  - Toprak/Drone: yalnızca kullanıcı yüklerse gerçek ölçümle; yoksa "yüklenince
    netleşir" — ASLA uydurulmaz.

Tek doğruluk kaynağı: tüm sayısal değerler ctx'ten f-string ile beslenir
(hardcoded sayı yok). Toprak yüklenince interpret_soil ile ölçülen durum
(düşük/ideal/yüksek) somut eyleme çevrilir; drone yüklenince CWSI/stres/VARI işlenir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from tarla_ai.advisory.models import OperationAdvice, SourceAction, Urgency
from tarla_ai.climate.analysis import analyze_by_stage, season_summary
from tarla_ai.climate.models import DailyWeather, SeasonSummary, StageWeatherSummary
from tarla_ai.climate.reference import GDD_TARGET_MAX, GDD_TARGET_MIN
from tarla_ai.drone.analysis import DroneAnalysis
from tarla_ai.soil.analysis import ParamStatus, interpret_soil
from tarla_ai.soil.parsing import SoilReport
from tarla_ai.water.reference import WELL_WATER_BASELINE

# Kaynak künyeleri (source, icon, label)
_SU     = ("su", "💧", "Su analizi")
_TOPRAK = ("toprak", "🧪", "Toprak analizi")
_DRONE  = ("drone", "🛰️", "Drone görüntüsü")
_HAVA   = ("hava", "🌤️", "Hava durumu")

# İşlem zaman pencereleri (ekim yılı sy'ye göre _win ile üretilir)
_SOWING_MONTH, _SOWING_DAY_END = 10, 20


def next_sowing_date(today: date) -> date:
    if today <= date(today.year, _SOWING_MONTH, _SOWING_DAY_END):
        return date(today.year, _SOWING_MONTH, 1)
    return date(today.year + 1, _SOWING_MONTH, 1)


def _win(sy: int, m1: int, d1: int, m2: int, d2: int) -> tuple[date, date]:
    y1 = sy if m1 >= 10 else sy + 1
    y2 = sy if m2 >= 10 else sy + 1
    return (date(y1, m1, d1), date(y2, m2, d2))


def _eta(start: date, today: date) -> str:
    d = (start - today).days
    if d < -3:
        return "zamanı geçti"
    if d <= 0:
        return "şu an"
    if d < 45:
        return f"~{d} gün sonra"
    return f"~{round(d / 30)} ay sonra"


def _urgency(start: date, end: date, today: date, soon_days: int = 35) -> Urgency:
    if start <= today <= end:
        return Urgency.NOW
    if today < start:
        return Urgency.SOON if (start - today).days <= soon_days else Urgency.INFO
    return Urgency.DONE


def _sa(meta: tuple[str, str, str], available: bool, *, state: str | None = None,
        toprak: str | None = None, bitki: str | None = None,
        value: str | None = None, missing: str | None = None) -> SourceAction:
    src, icon, label = meta
    if state is None:
        state = "baglandi" if available else "yuklenince"
    return SourceAction(src, icon, label, available, state, toprak, bitki, value, missing)


@dataclass(frozen=True)
class AdvisoryContext:
    today: date
    next_sowing: date
    days_to_sowing: int
    sowing_year: int
    ref_summary: SeasonSummary
    ref_stages: dict[str, StageWeatherSummary]
    has_soil: bool
    has_drone: bool
    soil_status: dict[str, ParamStatus] = field(default_factory=dict)
    drone: DroneAnalysis | None = None
    water_ec_ds_m: float | None = None


def build_context(
    days: list[DailyWeather], *,
    has_soil: bool = False, has_drone: bool = False,
    soil: SoilReport | None = None, drone: DroneAnalysis | None = None,
) -> AdvisoryContext:
    today = date.today()
    nso = next_sowing_date(today)
    soil_status: dict[str, ParamStatus] = {}
    if soil is not None:
        soil_status = {p.name: p for p in interpret_soil(soil).results}
    return AdvisoryContext(
        today=today, next_sowing=nso, days_to_sowing=(nso - today).days,
        sowing_year=nso.year,
        ref_summary=season_summary(days),
        ref_stages={s.stage_name: s for s in analyze_by_stage(days)},
        has_soil=has_soil, has_drone=has_drone,
        soil_status=soil_status, drone=drone,
        water_ec_ds_m=WELL_WATER_BASELINE.ec_ds_m,
    )


def _ref_rain(ctx: AdvisoryContext, stage: str) -> float | None:
    s = ctx.ref_stages.get(stage)
    return s.total_rain_mm if s and s.has_data else None


def _ps(ctx: AdvisoryContext, name: str) -> ParamStatus | None:
    return ctx.soil_status.get(name)


# ── Aşamalar ─────────────────────────────────────────────────────────────────

def advise_preparation(ctx: AdvisoryContext) -> OperationAdvice:
    ec = ctx.water_ec_ds_m
    rain12 = ctx.ref_summary.total_rain_mm
    # Toprak: yüklendiyse ölçülen önemli durumlar
    if ctx.has_soil and ctx.soil_status:
        lows = [p.name.split("(")[0].strip() for p in ctx.soil_status.values()
                if p.status == "düşük"]
        t_top = ("Ölçülen toprakta düşük çıkanlar: "
                 + (", ".join(lows) if lows else "yok")
                 + ". Taban gübre ve kireç planı bunlara göre kurulur.")
        toprak = _sa(_TOPRAK, True, toprak=t_top,
                     bitki="Eksik besinler ekimle/erken telafi edilir.",
                     value="yüklenen analiz")
    else:
        toprak = _sa(_TOPRAK, False, toprak="Toprak analizi PDF'i yükle → fosfor, "
                     "çinko, azot, kireç ve pH ölçülünce taban gübre + kireçleme kararı "
                     "sayısal netleşir.", missing="Lab raporunu soldan yükle.")
    return OperationAdvice(
        key="hazirlik", icon="📍", title="Şu An — Hazırlık & Veri Toplama",
        timing="Ekim öncesi (yaz–erken sonbahar)", eta="şu an", urgency=Urgency.NOW,
        headline="Önce toprak analizi yaptır ve yükle; ekime kadar tarla hazırlığını tamamla.",
        detail=f"Bugün {ctx.today.strftime('%d.%m.%Y')} — tarla henüz ekilmedi. Ekime "
               f"~{ctx.days_to_sowing} gün var. Bu dönemde: toprak analizi yaptır, "
               f"kıraca uygun sertifikalı çeşit/tohumluk seç, anız/tarla hazırlığı yap.",
        source_actions=[
            _sa(_SU, ec is not None,
                toprak=f"Kuyu suyu EC {ec:.2f} dS/m (orta-yüksek tuzlu); ekim öncesi "
                       f"can suyunu tuzlu kuyudan vermekten kaçın.",
                bitki="Çimlenme suyu için yağış nemine güven.",
                value=f"EC {ec:.2f} dS/m (gerçek kuyu kaydı)" if ec is not None else None),
            toprak,
            _sa(_DRONE, ctx.has_drone, state="beklemede",
                missing="Bitki çıkmadan drone anlamsız; çıkıştan sonra ilk uçuş planlanır."),
            _sa(_HAVA, True,
                toprak="Sonbahar yağış penceresini izle; toprakta tava (nem) oluşunca "
                       "ekim yapılır.",
                bitki="Çimlenme için toprak nemli ve >8–10 °C olmalı.",
                value=f"Open-Meteo: son 12 ayda {rain12:.0f} mm yağış (referans)"),
        ],
    )


def advise_sowing(ctx: AdvisoryContext) -> OperationAdvice:
    w = _win(ctx.sowing_year, 10, 1, 10, 20)
    ec = ctx.water_ec_ds_m
    cim = _ref_rain(ctx, "Çimlenme / Çıkış")
    # Toprak eylemi
    if ctx.has_soil and ctx.soil_status:
        p = _ps(ctx, "Alınabilir Fosfor (P₂O₅)")
        z = _ps(ctx, "Çinko (Zn)")
        bits = []
        if p:
            bits.append(f"Fosfor {p.value:g} kg/da ({p.status})")
        if z:
            bits.append(f"Çinko {z.value:g} mg/kg ({z.status})")
        t_top = ("Ölçülen: " + "; ".join(bits) + ". "
                 + ("Fosfor düşükse tüm P₂O₅'i taban ver. " if p and p.status == "düşük" else "")
                 + ("Çinko düşük → çinkolu DAP/ZnSO₄ ile taban ver." if z and z.status == "düşük"
                    else "")) if bits else "Ölçülen değerlerle taban gübre ayarlanır."
        toprak = _sa(_TOPRAK, True, toprak=t_top,
                     bitki="Eksik besin ekimle verilirse kök ve kardeşlenme güçlü başlar.",
                     value="yüklenen analiz")
    else:
        toprak = _sa(_TOPRAK, False,
                     toprak="Taban gübre türü/miktarı (DAP, P₂O₅, çinko) toprak analizine "
                            "bağlıdır.",
                     missing="Toprak analizi yükle → taban gübre dozu kesinleşir; yoksa "
                             "bölge ortalaması uygulanır (referans).")
    return OperationAdvice(
        key="ekim", icon="🌱", title="Ekim (Tohum + Taban Gübre)",
        timing=f"Ekim {ctx.sowing_year} · 1.–2. hafta · BBCH 00–10",
        eta=_eta(w[0], ctx.today), urgency=_urgency(*w, ctx.today),
        headline="Ekimi Ekim ayının ilk yarısında nemli toprağa yap; tüm fosforu ekimle "
                 "taban ver.",
        detail="Sıra arası ~17–20 cm, 18–22 kg/da tohum, ~3 kg N/da (DAP) taban. Kuru "
               "toprağa ekme; çıkış için tava (nem) şart. (Tohum/sıra değerleri referanstır.)",
        source_actions=[
            _sa(_SU, ec is not None,
                toprak=f"EC {ec:.2f} tuzlu → çıkış (can) suyunu kuyudan verme.",
                bitki="Tuzlu can suyu çimlenmeyi geciktirir; yağışa güven.",
                value=f"EC {ec:.2f} dS/m" if ec is not None else None),
            toprak,
            _sa(_DRONE, ctx.has_drone, state="beklemede",
                missing="Ekimde drone kullanılmaz; çıkış sonrası devreye girer."),
            _sa(_HAVA, True,
                toprak="Ekim öncesi yağış/sıcaklıkla tava ve sıcaklık uygunluğu izlenir.",
                bitki="Çimlenme için toprak >8–10 °C ve nemli olmalı.",
                value=(f"Referans: geçen yıl Eki–Kas ~{cim:.0f} mm" if cim is not None
                       else "Open-Meteo (gerçek)")),
        ],
    )


def advise_fertilization(ctx: AdvisoryContext) -> OperationAdvice:
    w = _win(ctx.sowing_year, 2, 15, 3, 15)
    ec = ctx.water_ec_ds_m
    kar = _ref_rain(ctx, "Kardeşlenme")
    if ctx.has_soil and ctx.soil_status:
        n = _ps(ctx, "Toplam Azot")
        om = _ps(ctx, "Organik Madde")
        bits = []
        if n:
            bits.append(f"toplam azot %{n.value:g} ({n.status})")
        if om:
            bits.append(f"organik madde %{om.value:g} ({om.status})")
        t_top = ("Ölçülen: " + "; ".join(bits) + ". Azot/organik madde düşükse üst azotu "
                 "referans aralığın üst sınırına çek." if bits
                 else "Ölçülen değerlere göre üst azot ayarlanır.")
        toprak = _sa(_TOPRAK, True, toprak=t_top,
                     bitki="Azot eksikse yapraklar sararır, kardeş azalır — doz buna göre.",
                     value="yüklenen analiz")
    else:
        toprak = _sa(_TOPRAK, False,
                     toprak="Kesin üst azot miktarı (kg N/da) toprağın azot/organik madde "
                            "ölçümüne bağlıdır.",
                     missing="Toprak analizi yükle → kg N/da kişiselleşir; yoksa kıraç "
                             "referansı ~6–10 kg N/da toplam kullanılır.")
    if ctx.has_drone and ctx.drone is not None and ctx.drone.vari_mean is not None:
        drone = _sa(_DRONE, True,
                    bitki=f"Yeşillik (VARI {ctx.drone.vari_mean:.2f}) haritası zayıf/sarı "
                          f"bölgeleri gösterir → oralara değişken oranlı (VRA) fazla azot.",
                    value=f"VARI {ctx.drone.vari_mean:.2f}")
    else:
        drone = _sa(_DRONE, False,
                    missing="Çıkış sonrası drone yükle → yeşillik haritası eksik-azot "
                            "bölgelerini gösterir, değişken oranlı (VRA) gübreleme yapılır.")
    return OperationAdvice(
        key="gubre", icon="🧪", title="Gübreleme (Üst Azot)",
        timing=f"Kardeşlenme–sapa kalkma ({ctx.sowing_year+1} Şub–Nis) · BBCH 20–39",
        eta=_eta(w[0], ctx.today), urgency=_urgency(*w, ctx.today),
        headline="Üst azotu 2–3 parçaya bölerek, her zaman yağıştan hemen önce ver.",
        detail="Azotu kardeşlenme (1. üst) ve sapa kalkma (2. üst) olarak parçalı ver. "
               "Kuru toprağa serpilen azot buharlaşır. Bayrak yaprak sonrası topraktan "
               "azot verme. (Doz aralıkları kıraç referansıdır.)",
        source_actions=[
            _sa(_SU, ec is not None,
                toprak=f"Tuzlu kuyu (EC {ec:.2f}) ile yıkama/fertigasyon yapma; azotu kuru "
                       f"gübre olarak yağış öncesi ver.",
                value=f"EC {ec:.2f} dS/m" if ec is not None else None),
            toprak, drone,
            _sa(_HAVA, True,
                toprak="Üst azotu yağıştan hemen önce ver (kuru toprakta N kaybolur).",
                bitki="Yağışla inen azot kök bölgesinden alınır.",
                value=(f"Referans: kardeşlenmede ~{kar:.0f} mm yağış" if kar is not None
                       else "Open-Meteo (gerçek)")),
        ],
    )


def advise_spraying(ctx: AdvisoryContext) -> OperationAdvice:
    w = _win(ctx.sowing_year, 2, 20, 5, 20)
    basak = ctx.ref_stages.get("Bayrak Yaprak / Başaklanma")
    hum = basak.avg_humidity_pct if basak and basak.has_data else None
    wind = ctx.ref_summary.max_wind_kmh
    if ctx.has_drone and ctx.drone is not None:
        sr = ctx.drone.stress_ratio
        vari = ctx.drone.vari_mean
        if sr is not None:
            d_bitki = (f"Termal stres haritası: alanın %{sr*100:.0f}'i stresli → sorunlu "
                       f"bölgelere hedefli ilaçlama (ilaç tasarrufu).")
            d_val = f"stresli alan %{sr*100:.0f}"
        elif vari is not None:
            d_bitki = (f"Yeşillik (VARI {vari:.2f}) düşük lekeler hastalık/ot şüphesi → "
                       f"o bölgeleri öncelikli kontrol/ilaçla.")
            d_val = f"VARI {vari:.2f}"
        else:
            d_bitki = "Yüklenen görüntüde anlamlı stres/lekeleme metriği çıkmadı."
            d_val = "yüklenen görüntü"
        drone = _sa(_DRONE, True, bitki=d_bitki, value=d_val)
    else:
        drone = _sa(_DRONE, False,
                    bitki="Drone yükle → hastalık/yabancı ot lekeleri ve canlılık haritasıyla "
                          "yalnız sorunlu bölgeye ilaçlama (noktasal, ilaç tasarrufu).",
                    missing="Çıkış sonrası drone görüntüsü gerekir.")
    risk = None
    if hum is not None:
        risk = "yüksek" if hum >= 65 else "orta-düşük"
    return OperationAdvice(
        key="ilac", icon="🛡️", title="İlaçlama (Ot + Hastalık)",
        timing=f"{ctx.sowing_year+1} Şub–May · BBCH 20–51",
        eta=_eta(w[0], ctx.today), urgency=_urgency(*w, ctx.today),
        headline="İlaçlamayı rüzgârsız, serin saatte ve yağışsız pencerede yap.",
        detail="Önce kardeşlenmede yabancı ota karşı herbisit; sonra bayrak yaprak–"
               "başaklanmada nem yüksekse mantar (pas/septoria) için fungisit. İlaç saatini "
               "hava tahminine göre seç.",
        source_actions=[
            _sa(_HAVA, True,
                bitki=("İlaçlama penceresi: rüzgâr <15–20 km/sa, yağışsız 4–6 saat, çok "
                       "sıcak değil." + (f" Geçen yıl başaklanmada nem ~%{hum:.0f} → mantar "
                       f"riski {risk}." if hum is not None else "")),
                value=f"geçen yıl en yüksek rüzgâr {wind:.0f} km/sa (referans)"),
            drone,
            _sa(_TOPRAK, ctx.has_soil, state="beklemede",
                bitki="Toprak pH/kireç hastalık baskısını dolaylı etkiler (ikincil).",
                missing="İlaçlamada toprak verisi doğrudan kullanılmaz."),
            _sa(_SU, ctx.water_ec_ds_m is not None, state="beklemede",
                bitki="İlaç çözeltisi suyu çok tuzluysa etkinlik düşebilir (ikincil)."),
        ],
    )


def advise_irrigation(ctx: AdvisoryContext) -> OperationAdvice:
    w = _win(ctx.sowing_year, 3, 1, 6, 10)
    ec = ctx.water_ec_ds_m
    defi = ctx.ref_summary.water_deficit_mm
    sapa = _ref_rain(ctx, "Sapa Kalkma")
    # Drone: termal CWSI varsa
    if ctx.has_drone and ctx.drone is not None and ctx.drone.cwsi_mean is not None:
        drone = _sa(_DRONE, True,
                    toprak="Termal su-stresi (CWSI) haritası tarlanın neresinde stres "
                           "olduğunu gösterir → önce o bölgeyi sula.",
                    bitki=f"Ortalama CWSI {ctx.drone.cwsi_mean:.2f}; yüksek bölgeler susuz.",
                    value=f"CWSI {ctx.drone.cwsi_mean:.2f}")
    else:
        drone = _sa(_DRONE, False,
                    toprak="Drone (termal) yükle → tarla içi su-stresi haritasıyla hedefli "
                           "sulama bölgesi belirlenir.",
                    missing="Termal GeoTIFF gerekir.")
    # Toprak: yüklendiyse EC
    soil_ec = _ps(ctx, "EC / Tuzluluk")
    if ctx.has_soil and soil_ec is not None and ec is not None:
        toprak = _sa(_TOPRAK, True,
                     toprak=f"Toprak EC {soil_ec.value:g} dS/m + kuyu EC {ec:.2f} → tekrarlı "
                            f"sulamada tuz birikimi takip edilir; gerekirse yıkama payı artırılır.",
                     value=f"toprak EC {soil_ec.value:g} dS/m")
    else:
        toprak = _sa(_TOPRAK, False,
                     toprak="Toprak analizi yükle → toprak tuzu (EC) + tekstür ile net "
                            "sulama miktarı (mm) ve tuz birikimi riski hesaplanır.",
                     missing="Toprak EC/tekstür gerekir.")
    return OperationAdvice(
        key="sulama", icon="💧", title="Sulama",
        timing=f"Kritik dönem ({ctx.sowing_year+1} Mar–Haz) · BBCH 30–69",
        eta=_eta(w[0], ctx.today), urgency=_urgency(*w, ctx.today),
        headline="Sistem kıraç; sadece sapa kalkma–çiçeklenmede ciddi kuraklıkta, kontrollü "
                 "kurtarma sulaması yap.",
        detail="Asıl su kaynağı yağış. Kuyu suyu tuzlu olduğundan her dönemde verilemez; "
               "damla/yağmurlama ile yıkama payı bırak, salma sulamadan kaçın.",
        source_actions=[
            _sa(_SU, ec is not None,
                toprak=f"EC {ec:.2f} dS/m → salma değil damla/yağmurlama, yıkama payı bırak.",
                bitki="Kuyu suyu yalnız kritik kuraklık kurtarması; rutin sulama tuz stresi yapar.",
                value=f"EC {ec:.2f} dS/m (gerçek kuyu kaydı)" if ec is not None else None),
            _sa(_HAVA, True,
                toprak=f"Su dengesi (buharlaşma−yağış) {defi:+.0f} mm → sulama gerekli mi "
                       f"kararının temeli.",
                bitki=("Sapa kalkma en kritik su dönemi"
                       + (f"; geçen yıl ~{sapa:.0f} mm." if sapa is not None else ".")),
                value=f"su dengesi {defi:+.0f} mm (referans)"),
            toprak, drone,
        ],
    )


def advise_harvest(ctx: AdvisoryContext) -> OperationAdvice:
    w = _win(ctx.sowing_year, 7, 10, 7, 25)
    gdd = ctx.ref_summary.total_gdd
    return OperationAdvice(
        key="hasat", icon="🌾", title="Hasat",
        timing=f"{ctx.sowing_year+1} Temmuz 2. yarı · BBCH 89",
        eta=_eta(w[0], ctx.today), urgency=_urgency(*w, ctx.today),
        headline="Tane sertleşip nemi ~%13–14'e inince, Temmuz ikinci yarısında hasat et.",
        detail="Hasat zamanı tane nemiyle belirlenir: tane tırnakla ezilmiyorsa olgundur. "
               "Hasat öncesi son 2–3 hafta sulama yapma.",
        source_actions=[
            _sa(_HAVA, True,
                bitki=f"Sıcaklık birikimi (GDD) hedefi {GDD_TARGET_MIN:.0f}–{GDD_TARGET_MAX:.0f} "
                      f"°C·gün; olgunluk ve yağışsız hasat penceresi havadan takip edilir.",
                value=f"referans: son 12 ayda ~{gdd:.0f} °C·gün"),
            _sa(_SU, ctx.water_ec_ds_m is not None, state="beklemede",
                toprak="Hasat öncesi son 2–3 hafta sulama yapılmaz."),
            _sa(_TOPRAK, ctx.has_soil, state="beklemede",
                missing="Hasatta toprak verisi doğrudan kullanılmaz."),
            _sa(_DRONE, ctx.has_drone, state="beklemede" if not ctx.has_drone else "baglandi",
                bitki="Olgunluk/yatma haritası hasat sırası planlamasına yardımcı olabilir.",
                missing="İsteğe bağlı: olgunluk haritası."),
        ],
    )


def all_advice(
    days: list[DailyWeather], *,
    has_soil: bool = False, has_drone: bool = False,
    soil: SoilReport | None = None, drone: DroneAnalysis | None = None,
) -> list[OperationAdvice]:
    ctx = build_context(days, has_soil=has_soil, has_drone=has_drone, soil=soil, drone=drone)
    return [
        advise_preparation(ctx),
        advise_sowing(ctx),
        advise_fertilization(ctx),
        advise_spraying(ctx),
        advise_irrigation(ctx),
        advise_harvest(ctx),
    ]
