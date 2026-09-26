"""Schema-aware, offline handling of empty embedded objects at the Sanity boundary.

Canonical nulls remain in source JSON. Only optional or nullable object fields
may be omitted. Empty arrays, false, zero, and UNKNOWN remain meaningful values.
Arbitrary-value boxes and extension metadata retain their existing serialization.
"""
import copy
import json
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "02-schema-design/evidapath-schema-v1.2.json"


def has_meaningful_value(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(has_meaningful_value(v) for k, v in value.items()
                   if k not in {"_type", "_key"})
    # [] can mean verified absence; false and zero are actual facts.
    return True


def check_objects(document, *, omit_empty=False, schema=None):
    """Return (copy, issues); never mutate source data or strip required objects.

    Derive optionality from the owning property and referenced canonical type.
    Required-but-nullable canonical objects are optional at the Sanity boundary.
    Populated objects stay intact, including incomplete ones needing validation.
    """
    if schema is None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    defs = schema["$defs"]
    types = {name.split("_")[0] + "".join(p.title() for p in name.split("_")[1:]): name
             for name in defs}
    root = defs.get(types.get(document.get("_type")), {})
    issues = []

    def resolve(spec):
        return defs[spec["$ref"].split("/")[-1]] if "$ref" in spec else spec

    def walk(value, spec, path):
        spec = resolve(spec)
        if isinstance(value, dict):
            required = set(spec.get("required", []))
            for key, child_spec in spec.get("properties", {}).items():
                if key not in value:
                    continue
                child = value[key]
                resolved = resolve(child_spec)
                child_path = f"{path}.{key}" if path else key
                # These adapters encode arbitrary values; retain their separate
                # existing contracts (including explicit null/empty findings).
                if key == "extension_metadata" or not resolved:
                    continue
                if isinstance(child, dict) and "properties" in resolved:
                    nullable = "null" in resolved.get("type", [])
                    optional = key not in required or nullable
                    if not has_meaningful_value(child):
                        if omit_empty and optional:
                            del value[key]
                            continue
                        issues.append({"path": child_path, "optional": optional,
                                       "object_type": child.get("_type")})
                    else:
                        walk(child, resolved, child_path)
                elif isinstance(child, list):
                    walk(child, resolved, child_path)
        elif isinstance(value, list) and "items" in spec:
            for i, child in enumerate(value):
                walk(child, spec["items"], f"{path}[{i}]")

    result = copy.deepcopy(document)
    walk(result, root, "")
    return result, issues
