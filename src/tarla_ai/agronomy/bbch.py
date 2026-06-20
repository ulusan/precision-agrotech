"""BBCH fenolojik büyüme takvimi — ekmeklik buğday."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BbchStage:
    """Tek BBCH aşaması: kod, isim, kısa açıklama, detay, görevler."""

    code: str
    name: str
    short: str
    description: str
    tasks: tuple[tuple[str, str], ...]   # (renk, metin) çiftleri


BBCH_STAGES: tuple[BbchStage, ...] = (
    BbchStage("00", "Çimlenme", "Ekim — Çimlenme",
              "Tohum toprağa verilir; su alımıyla şişme ve çimlenme başlar. "
              "Toprak nemi homojen olmalı, ekim derinliği 3–5 cm idealdir.",
              (("green", "Tohum yatağı hazırlığını kontrol et"),
               ("green", "Ekim derinliğini 3–5 cm ayarla"),
               ("green", "Tüm fosforu (6–8 kg/da) ekimle taban gübresi olarak ver"),
               ("amber", "Çinko eksikse çinkolu DAP kullan"))),

    BbchStage("10", "Çıkış", "Çıkış",
              "İlk yaprak toprak yüzeyini deler; bitki fotosenteze başlar. "
              "Çıkış oranı ve homojenliği verim tahmini için kritik veridir.",
              (("green", "Çıkış sayımı yap ve homojenliği değerlendir"),
               ("green", "Yabancı ot baskısını kontrol et"),
               ("amber", "Erken don riski varsa önlem al"),
               ("amber", "Çıkış oranını kaydet (%)"))),

    BbchStage("20", "Kardeşlenme", "Kardeşlenme",
              "Ana sapın yanında yeni yan saplar (kardeş) oluşur. "
              "Kardeş sayısı verim potansiyelini doğrudan belirler; "
              "azot ihtiyacı bu dönemde artmaya başlar.",
              (("green", "Kardeş sayısını say (hedef: 3–5 kardeş/bitki)"),
               ("red",   "1. üst gübre azot uygula (2–4 kg N/da) — yağış öncesi"),
               ("amber", "Herbisit uygulaması için uygun pencereyi belirle"),
               ("amber", "Kışlık ekimde don zararını kontrol et"))),

    BbchStage("30", "Sapa Kalkma", "Sapa Kalkma",
              "Bitki boyunu hızla artırır; boğumlar birbirinden uzaklaşır. "
              "Azot ve su ihtiyacı bu evrede en yüksek noktadadır. "
              "Bu dönemdeki kuraklık verimi en çok düşürür.",
              (("red",   "2. üst gübre azot uygula (2–3 kg N/da)"),
               ("red",   "Su stresini izle — en kritik su dönemi"),
               ("amber", "Yatma riskine karşı büyüme düzenleyici değerlendir"),
               ("green", "Fungisit ihtiyacını değerlendir"))),

    BbchStage("37", "Bayrak Yaprak", "Bayrak Yaprak",
              "Son yaprak (bayrak yaprağı) açılır; bu yaprak tane dolumunun "
              "ana fotosentez kaynağıdır. Azot alımı en üst düzeydedir.",
              (("red",   "Bayrak yaprağı hastalıklarını (pas, septoria) izle"),
               ("amber", "Gerekirse yapraktan üre/Zn takviyesi (protein için)"),
               ("green", "Yaprak alan indeksini değerlendir"),
               ("green", "Su durumunu kontrol et"))),

    BbchStage("51", "Başaklanma", "Başaklanma",
              "Başak yaprak kılıfından çıkmaya başlar. Hastalık baskısının "
              "arttığı dönemdir; özellikle sarı pas ve septoria izlenmelidir.",
              (("red",   "Fungisit uygulaması — sarı pas ve septoria"),
               ("amber", "Başak gelişimini ve homojenliği izle"),
               ("green", "Yaprak alan indeksini değerlendir"),
               ("amber", "Dolu ve aşırı yağış riskini takip et"))),

    BbchStage("65", "Çiçeklenme", "Çiçeklenme",
              "Başağın yarısından fazlasında çiçeklenme tamamlanmıştır. "
              "Su stresine en hassas dönemdir; fusarium riski maksimuma ulaşır.",
              (("red",   "Fusarium'a karşı fungisit uygula — kritik pencere"),
               ("red",   "Su stresini izle — döllenmeyi doğrudan etkiler"),
               ("amber", "Sıcaklık + nem kombinasyonunu izle (fusarium)"),
               ("green", "Çiçeklenme homojenliğini kaydet"))),

    BbchStage("75", "Tane Dolumu", "Tane Dolumu",
              "Daneler dolar; süt ve hamur olum aşamalarından geçer. "
              "Su ve sıcaklık stresi dane ağırlığını düşürür.",
              (("amber", "Dane dolum hızını izle"),
               ("amber", "Geç dönem yapraktan üre — tane proteini için"),
               ("green", "Kuş ve zararlı baskısını kontrol et"),
               ("green", "Hasat ekipmanı bakımını planla"))),

    BbchStage("89", "Sarı Olum", "Sarı Olum",
              "Daneler sarılaşır, nem düşer. Hasat zamanlaması ve lojistiği "
              "planlanmalıdır; gecikme kayıp riskini artırır.",
              (("amber", "Dane nemini ölç (hedef: %14–16 hasat için)"),
               ("amber", "Hasat zamanlamasını hava durumuna göre planla"),
               ("green", "Kurutma ve depolama kapasitesini hazırla"),
               ("green", "Hasat sonrası toprak analizi planla (sonraki sezon)"))),
)
