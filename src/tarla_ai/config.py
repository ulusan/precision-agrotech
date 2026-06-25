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

    # Hedef koordinat sistemi
    target_crs: str = "EPSG:4326"

    # ── Kullanıcı yüklemeleri (UI'dan gelen analizler) ─────────────────────
    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def soil_uploads_dir(self) -> Path:
        return self.uploads_dir / "soil"

    @property
    def water_uploads_dir(self) -> Path:
        return self.uploads_dir / "water"

    @property
    def drone_uploads_dir(self) -> Path:
        return self.uploads_dir / "drone"

    # ── CLI / pipeline çıktıları ────────────────────────────────────────────
    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    # ── Referans belgeler (sadece okunur, commit edilir) ────────────────────
    @property
    def references_dir(self) -> Path:
        return REPO_ROOT / "docs" / "references"

    def ensure_dirs(self) -> None:
        """Veri dizinlerini oluştur (yoksa)."""
        for d in (
            self.soil_uploads_dir,
            self.water_uploads_dir,
            self.drone_uploads_dir,
            self.processed_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
