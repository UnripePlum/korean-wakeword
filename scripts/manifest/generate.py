from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.manifest.core import (  # noqa: E402
    ManifestError,
    build_manifest,
    check_manifest,
    render_manifest,
    write_manifest,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate or validate wake_word_manifest.json from artifact folders."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        type=Path,
        help="Repository root containing artifact folders.",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--write",
        action="store_true",
        help="Write wake_word_manifest.json at the repository root.",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Fail if wake_word_manifest.json is missing, invalid, or out of date.",
    )

    args = parser.parse_args(argv)

    try:
        if args.write:
            path = write_manifest(args.repo_root)
            print(f"wrote {path}")
            return 0
        if args.check:
            check_manifest(args.repo_root)
            print("wake_word_manifest.json is valid")
            return 0

        print(render_manifest(build_manifest(args.repo_root)), end="")
        return 0
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
