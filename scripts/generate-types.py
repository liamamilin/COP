#!/usr/bin/env python3
"""Generate the browser's TypeScript contract from the canonical COP schema."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "cop-artifact.schema.json"
OUTPUT_PATH = ROOT / "packages" / "cop-types" / "generated" / "index.ts"

COLLECTION_NAMES = {
    "goals": "Goal",
    "shared_foundations": "SharedFoundation",
    "main_processes": "MainProcess",
    "stages": "Stage",
    "concepts": "Concept",
    "operations": "Operation",
    "branches": "Branch",
    "practices": "Practice",
    "expansion_map": "ExpansionItem",
}


def ts_type(schema: dict[str, Any], *, indent: int = 0) -> str:
    if "$ref" in schema:
        return str(schema["$ref"]).rsplit("/", 1)[-1]
    if "const" in schema:
        return json.dumps(schema["const"], ensure_ascii=False)
    if "enum" in schema:
        return " | ".join(json.dumps(item, ensure_ascii=False) for item in schema["enum"])
    kind = schema.get("type")
    if isinstance(kind, list):
        return " | ".join(ts_type({**schema, "type": item}, indent=indent) for item in kind)
    if kind == "string":
        return "string"
    if kind in {"integer", "number"}:
        return "number"
    if kind == "boolean":
        return "boolean"
    if kind == "null":
        return "null"
    if kind == "array":
        item_type = ts_type(schema.get("items") or {}, indent=indent)
        return f"({item_type})[]" if " | " in item_type else f"{item_type}[]"
    if kind == "object":
        properties = schema.get("properties") or {}
        if not properties:
            return "Record<string, unknown>"
        required = set(schema.get("required") or [])
        pad = " " * indent
        child = " " * (indent + 2)
        lines = ["{"]
        for name, value in properties.items():
            optional = "" if name in required else "?"
            lines.append(f"{child}{name}{optional}: {ts_type(value, indent=indent + 2)};")
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    return "unknown"


def interface(name: str, schema: dict[str, Any]) -> str:
    required = set(schema.get("required") or [])
    lines = [f"export interface {name} {{"]
    for field, value in (schema.get("properties") or {}).items():
        optional = "" if field in required else "?"
        rendered = ts_type(value, indent=2)
        lines.append(f"  {field}{optional}: {rendered};")
    lines.append("}")
    return "\n".join(lines)


def generate(schema: dict[str, Any]) -> str:
    blocks = [
        "/* Generated from schemas/cop-artifact.schema.json. Do not edit by hand. */"
    ]
    for name, definition in (schema.get("$defs") or {}).items():
        blocks.append(interface(name, definition))
    for property_name, interface_name in COLLECTION_NAMES.items():
        blocks.append(interface(interface_name, schema["properties"][property_name]["items"]))

    root_properties = dict(schema["properties"])
    for property_name, interface_name in COLLECTION_NAMES.items():
        root_properties[property_name] = {
            "type": "array",
            "items": {"$ref": f"#/$defs/{interface_name}"},
        }
    root = {**schema, "properties": root_properties}
    blocks.append(interface("COPArtifact", root))
    return "\n\n".join(blocks) + "\n"


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.write_text(generate(schema), encoding="utf-8")


if __name__ == "__main__":
    main()
