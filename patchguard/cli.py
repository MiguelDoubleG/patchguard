"""Command-line interface: python -m patchguard [data_dir]"""

import argparse
import sys
from pathlib import Path
from patchguard.preview import build_preview

from patchguard.validate import validate_champion_file, validate_items_file


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="patchguard",
        description="Check game content files for mistakes before they ship.",
    )
    parser.add_argument(
        "data_dir",
        nargs="?",
        default="data",
        help="folder that holds champions/ and items.yaml (default: data)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="only print files that fail"
    )
    parser.add_argument(
        "--preview",
        metavar="FILE",
        help="also write an HTML page with a card for each champion and item",
    )
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir)
    if not data_dir.is_dir():
        print(f"error: folder not found: {data_dir}", file=sys.stderr)
        return 2

    results = []
    for path in sorted(data_dir.glob("champions/*.yaml")):
        results.append((path, validate_champion_file(path)))
    items_path = data_dir / "items.yaml"
    if items_path.exists():
        results.append((items_path, validate_items_file(items_path)))

    failed_files = 0
    total_errors = 0
    for path, errors in results:
        if errors:
            failed_files += 1
            total_errors += len(errors)
            print(f"FAIL {path}")
            for message in errors:
                print(f"     {message}")
        elif not args.quiet:
            print(f"OK   {path}")
    if args.preview:
        Path(args.preview).write_text(build_preview(results),encoding="utf-8")
        print(f"Preview written to {args.preview}")
    print(f"\n{len(results)} files checked, {failed_files} failed, {total_errors} errors")
    return 1 if failed_files else 0