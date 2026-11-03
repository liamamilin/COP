#!/usr/bin/env python3
"""Check/generate experimental schema and types; never change the COP 0.1 schema.

Run with the backend's environment. Default is a drift check; --write updates only
the two explicitly named generated files. Candidate instructions are never run.
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.domain.learning_unit import LearningUnit  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location(
        "generate_types", ROOT / "scripts/generate-types.py",
    )
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://cop-studio.local/schemas/learning-unit.experimental.schema.json",
        **LearningUnit.model_json_schema(),
    }
    schema_path = ROOT / "schemas/learning-unit.experimental.schema.json"
    documents = {
        schema_path: json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
        ROOT / "packages/cop-types/generated/learning-unit.ts": generator.generate_document(
            schema, "LearningUnit", str(schema_path.relative_to(ROOT)),
        ),
    }
    for path, content in documents.items():
        if args.write:
            path.write_text(content, encoding="utf-8")
        elif not path.exists() or path.read_text(encoding="utf-8") != content:
            raise SystemExit(f"Generated file drift: {path.relative_to(ROOT)} (use --write)")
    print("Experimental learning-unit schema/types match; COP 0.1 is unchanged.")


if __name__ == "__main__":
    main()
