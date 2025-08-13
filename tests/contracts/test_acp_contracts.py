import json
from pathlib import Path


SCHEMA_DIR = Path(__file__).resolve().parents[2] / "docs" / "data" / "schema-registry" / "v1" / "acp"


def test_acp_schemas_exist():
    expected = ["task.json", "result.json", "event.json", "heartbeat.json"]
    for name in expected:
        path = SCHEMA_DIR / name
        assert path.exists(), f"Missing schema: {path} (run: python scripts/export_schemas.py)"
        # basic sanity check: loadable JSON
        json.loads(path.read_text(encoding="utf-8"))


