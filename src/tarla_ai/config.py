"""Proje genel yapilandirmasi ve dizin yollari.

Tum yollar buradan tek noktadan yonetilir; modullerde sabit string yol kullanma.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo koku: src/tarla_ai/config.py -> ../../.. = repo koku
REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Cevre degiskenleriyle override edilebilen proje ayarlari.

    .env dosyasi veya TARLA_ onekli cevre degiskenleri ile ezilebilir.
    Ornek: TARLA_DATA_DIR=/mnt/veri
    """

    model_config = SettingsConfigDict(
        env_prefix="TARLA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    data_dir: Path = REPO_ROOT / "data"

    # Hedef koordinat sistemi - Turkiye geneli icin UTM Zone 35N / 36N veya
    # tek tarla pilot icin parselin bulundugu zona gore secilir.
    # Varsayilan: WGS84 (kaynak veriden geldigi gibi); is akisinda projelendirilir.
    target_crs: str = "EPSG:4326"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def interim_dir(self) -> Path:
        return self.data_dir / "interim"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    def ensure_dirs(self) -> None:
        """Veri dizinlerini olustur (yoksa)."""
        for d in (self.raw_dir, self.interim_dir, self.processed_dir):
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
