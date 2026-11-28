#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import resvg_py
from excalidraw_render.render import load_scene, render_svg


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch-export .excalidraw files to PNG or SVG without Cairo."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="figures",
        help="Directory containing .excalidraw files (default: figures)",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["png", "svg"],
        default="png",
        help="Output format (default: png)",
    )
    parser.add_argument(
        "-z", "--zoom",
        type=float,
        default=2.0,
        help="PNG scale multiplier (default: 2.0)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-export even if the output file is newer than the .excalidraw file",
    )
    args = parser.parse_args()

    target_dir = Path(args.directory)
    if not target_dir.is_dir():
        print(f"Error: directory not found: {target_dir}", file=sys.stderr)
        return 1

    files = sorted(target_dir.rglob("*.excalidraw"))
    if not files:
        print(f"No .excalidraw files found in {target_dir}")
        return 0

    exported = 0
    skipped = 0

    for src in files:
        dst = src.with_suffix(f".{args.format}")
        if not args.force and dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            print(f"[skip]   {src} (up to date)")
            skipped += 1
            continue

        print(f"[export] {src} -> {dst}")
        scene = load_scene(str(src))
        svg_str = render_svg(scene)
        if args.format == "svg":
            dst.write_text(svg_str, encoding="utf-8")
        else:
            png_bytes = resvg_py.svg_to_bytes(svg_string=svg_str, zoom=args.zoom)
            dst.write_bytes(png_bytes)
        exported += 1

    print(f"\nDone: {exported} exported, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())