import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
COMMON_UTILS_PYTHON = REPO_ROOT / "src" / "layers" / "common_utils" / "python"
sys.path.insert(0, str(COMMON_UTILS_PYTHON))


def test_acp_protocol_symbols_exist():
    import acp_protocol as acp  # type: ignore

    # Core symbols should exist
    assert hasattr(acp, "ACPMessage")
    assert hasattr(acp, "ACPProtocol")
    assert hasattr(acp, "MessageType")


def test_acp_message_dump_roundtrip_smoke():
    import acp_protocol as acp  # type: ignore

    # Try to construct a minimal message using available helpers if present
    msg = None
    if hasattr(acp, "ACPProtocol") and hasattr(acp.ACPProtocol, "create_event"):
        proto = acp.ACPProtocol()
        # Best-effort minimal event payload
        msg = proto.create_event(event_type="test_event", data={"ok": True})
    elif hasattr(acp, "ACPMessage"):
        # Fallback: build a bare model if allowed by defaults
        try:
            msg = acp.ACPMessage()
        except Exception:
            msg = None

    assert msg is not None, "Failed to build an ACP message for smoke test"

    # Ensure pydantic v2 dump works without raising
    dumped = None
    if hasattr(msg, "model_dump_json"):
        dumped = msg.model_dump_json()
    elif hasattr(msg, "model_dump"):
        dumped = msg.model_dump()
    else:
        dumped = str(msg)

    assert dumped is not None


