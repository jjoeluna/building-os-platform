import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DEFAULT = REPO_ROOT / "src" / "tools" / "websocket_default"
sys.path.insert(0, str(TOOLS_DEFAULT))


def test_default_handler_has_log_model_reference():
    # Ensure handler module imports structured logging models or uses them
    import app  # type: ignore

    src = (TOOLS_DEFAULT / "app.py").read_text(encoding="utf-8")
    assert "StructuredLog" in src or "StructuredLogger" in src or "Structured" in src


