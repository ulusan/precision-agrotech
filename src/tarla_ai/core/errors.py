"""tarla_ai hata hiyerarşisi."""

from __future__ import annotations


class TarlaError(Exception):
    """Tüm tarla_ai hatalarının tabanı."""


class RasterFormatError(TarlaError):
    """GeoTIFF format veya bant sayısı uyumsuzluğu."""


class SoilParseError(TarlaError):
    """PDF'den toprak parametresi çıkarılamadı."""
