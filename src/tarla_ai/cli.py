"""tarla_ai komut satiri arayuzu.

Kullanim:
    tarla rgb-indices  rgb_orthomosaic.tif  --out-dir data/processed
    tarla cwsi  thermal.tif  --t-wet 18.5 --t-dry 32.0 --out data/processed/cwsi.tif
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tarla_ai import __version__
from tarla_ai.drone.indices import cwsi, exg, tgi, vari
from tarla_ai.core.raster import read_band, read_rgb, write_single_band


def _cmd_rgb_indices(args: argparse.Namespace) -> None:
    r, g, b, profile = read_rgb(args.input, normalize=not args.no_normalize)
    out_dir = Path(args.out_dir)
    outputs = {"vari": vari(r, g, b), "tgi": tgi(r, g, b), "exg": exg(r, g, b)}
    for name, arr in outputs.items():
        path = out_dir / f"{name}.tif"
        write_single_band(arr, path, profile)
        print(f"[ok] {name} -> {path}")


def _cmd_cwsi(args: argparse.Namespace) -> None:
    canopy, profile = read_band(args.input)
    result = cwsi(canopy, t_wet=args.t_wet, t_dry=args.t_dry)
    write_single_band(result, args.out, profile)
    print(f"[ok] CWSI -> {args.out}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tarla", description="Hassas tarim pipeline")
    parser.add_argument("--version", action="version", version=f"tarla-ai {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_rgb = sub.add_parser("rgb-indices", help="RGB ortomosaikten VARI/TGI/ExG")
    p_rgb.add_argument("input", help="3 bantli RGB GeoTIFF")
    p_rgb.add_argument("--out-dir", default="data/processed")
    p_rgb.add_argument("--no-normalize", action="store_true", help="0-255 boleme yapma")
    p_rgb.set_defaults(func=_cmd_rgb_indices)

    p_cwsi = sub.add_parser("cwsi", help="Termal goruntuden CWSI")
    p_cwsi.add_argument("input", help="Radyometrik termal GeoTIFF (Celsius)")
    p_cwsi.add_argument("--t-wet", type=float, required=True)
    p_cwsi.add_argument("--t-dry", type=float, required=True)
    p_cwsi.add_argument("--out", default="data/processed/cwsi.tif")
    p_cwsi.set_defaults(func=_cmd_cwsi)

    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
