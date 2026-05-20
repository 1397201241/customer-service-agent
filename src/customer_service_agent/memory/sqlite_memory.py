"""SQLite-backed conversation memory for the customer service agent."""

from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_DB_PATH = DATA_DIR / "chat_history.db"


# Module-level singleton checkpointer
_checkpointer: InMemorySaver | None = None


def get_checkpointer() -> InMemorySaver:
    """Get an InMemorySaver checkpointer for conversation persistence.

    Uses a module-level singleton.

    Returns:
        InMemorySaver instance.
    """
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = InMemorySaver()
    return _checkpointer
