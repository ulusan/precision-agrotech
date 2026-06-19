"""Literature dayali esik degerleri (Belge Bolum 5.1 / 9.4).

ONEMLI: Bu esikler literatur referansidir. Belge sonunda belirtildigi gibi
"saha kosullarina gore kalibre edilmesi onerilir". Kalibrasyon sonrasi bu
sabitler .env veya config ile override edilebilir hale getirilmeli.
"""

from __future__ import annotations

# Azot eksikligi: NDRE bu degerin altinda -> gubreleme onerisi (Belge 9.4)
NITROGEN_NDRE_THRESHOLD: float = 0.2

# Saglikli toprak pH araligi (bugday/arpa icin tipik notr-hafif alkali)
SOIL_PH_HEALTHY_MIN: float = 6.0
SOIL_PH_HEALTHY_MAX: float = 7.5

# CWSI su stresi esigi (Belge 10.8)
CWSI_STRESS_THRESHOLD: float = 0.5
