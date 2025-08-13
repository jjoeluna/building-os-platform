"""Export JSON Schemas from Pydantic models (ACP) into docs/data/schema-registry/v1/acp/.

Run inside repo root with venv active:
  python scripts/export_schemas.py
"""
from __future__ import annotations

from pathlib import Path
import json
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "docs" / "data" / "schema-registry" / "v1" / "acp"


def main() -> int:
    try:
        # Import from layer sources within repo (common_utils python path)
        sys.path.insert(0, str(REPO_ROOT / "src" / "layers" / "common_utils" / "python"))
        import acp_protocol  # type: ignore
    except Exception as exc:
        print(f"ERROR: failed to import acp_protocol: {exc}")
        return 1

    models = {
        "task.json": getattr(acp_protocol, "ACPTask", None),
        "result.json": getattr(acp_protocol, "ACPResult", None),
        "event.json": getattr(acp_protocol, "ACPEvent", None),
        "heartbeat.json": getattr(acp_protocol, "ACPHeartbeat", None),
        # fallback to generic ACPMessage if specific not found
    }

    # If specific models not present, derive schemas from ACPMessage with examples
    base_message = getattr(acp_protocol, "ACPMessage", None)
    if base_message is not None:
        for key, model in list(models.items()):
            if model is None:
                models[key] = base_message

    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for filename, model in models.items():
        if model is None:
            print(f"WARN: model for {filename} not found; skipping")
            continue
        try:
            schema = model.model_json_schema()
        except Exception:
            # pydantic v2 compatible alias
            schema = model.model_json_schema()  # type: ignore
        (SCHEMA_DIR / filename).write_text(json.dumps(schema, indent=2), encoding="utf-8")
        print(f"Wrote {SCHEMA_DIR / filename}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


