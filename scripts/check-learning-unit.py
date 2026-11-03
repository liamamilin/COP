#!/usr/bin/env python3
"""Read two local JSON documents and emit a structure-only manifest to stdout.

Usage: backend environment's python scripts/check-learning-unit.py UNIT ARTIFACT
Exit 1 for contract issues, 2 for unreadable input. Never runs candidate methods.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.domain.learning_unit import unit_manifest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unit", type=Path)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    try:
        unit = json.loads(args.unit.read_text(encoding="utf-8"))
        artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
        result = unit_manifest(unit, artifact)
    except (OSError, ValueError, TypeError) as error:
        print(f"Unable to check documents: {error}", file=sys.stderr)
        raise SystemExit(2) from error
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["issues"] else 0)


if __name__ == "__main__":
    main()
