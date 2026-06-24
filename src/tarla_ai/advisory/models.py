"""Öneri modelleri — her aşamada 4 veri kaynağının toprağa/bitkiye eylem eşlemesi."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Urgency(StrEnum):
    """Bir işlemin bugün itibarıyla durumu."""

    NOW = "now"
    SOON = "soon"
    DONE = "done"
    WATCH = "watch"
    INFO = "info"


URGENCY_LABEL: dict[Urgency, str] = {
    Urgency.NOW:   "ŞİMDİ",
    Urgency.SOON:  "YAKLAŞIYOR",
    Urgency.DONE:  "TAMAMLANDI",
    Urgency.WATCH: "DİKKAT / İZLE",
    Urgency.INFO:  "SIRADA",
}


@dataclass(frozen=True)
class SourceAction:
    """Bir veri kaynağının bir aşamada toprağa/bitkiye yönelik somut katkısı.

    DÖRT kaynak: su analizi, toprak analizi, drone görüntüsü, hava durumu.
    - available=True  → gerçek veri var (Open-Meteo / kuyu kaydı / yüklenen rapor).
    - available=False → veri yok; toprak_action/bitki_action None, missing_note dolu.
      ASLA uydurma değer üretilmez.
    state: 'baglandi' (gerçek veri akıyor) | 'yuklenince' (yüklenince gelir)
           | 'beklemede' (bu aşamada gerekli değil / zamanı değil).
    """

    source: str            # 'su' | 'toprak' | 'drone' | 'hava'
    icon: str
    label: str
    available: bool
    state: str
    toprak_action: str | None = None   # TOPRAĞA somut eylem
    bitki_action: str | None = None    # BİTKİYE somut eylem
    value_used: str | None = None      # kullanılan gerçek değer (ör. "EC 2.90 dS/m")
    missing_note: str | None = None    # veri yoksa: yüklenince ne olur


@dataclass(frozen=True)
class OperationAdvice:
    """Bir tarla aşaması için tavsiye + 4 kaynağın eylem eşlemesi."""

    key: str
    icon: str
    title: str
    timing: str
    urgency: Urgency
    headline: str
    detail: str
    eta: str = ""
    source_actions: list[SourceAction] = field(default_factory=list)

    @property
    def urgency_label(self) -> str:
        return URGENCY_LABEL[self.urgency]
