# GDAL/PROJ sistem bagimliliklarini hazir getiren resmi imaj uzerine kuruyoruz;
# boylece rasterio/geopandas derlemesi sorunsuz olur (Belge pratik tavsiye).
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.4

# Python + uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-dev build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# uv kur (Astral - pip'ten 10-100x hizli)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Bagimlilik katmani (kod degisince yeniden cozulmesin diye once kopyala)
COPY pyproject.toml ./
COPY uv.lock* ./
RUN uv sync --no-dev --no-install-project || uv sync --no-dev

# Uygulama kodu
COPY src ./src
COPY README.md ./
RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["tarla"]
CMD ["--help"]
