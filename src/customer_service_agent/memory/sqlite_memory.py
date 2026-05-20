"""SQLite-backed conversation memory for the customer service agent."""

from pathlib import Path

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_DB_PATH = DATA_DIR / "chat_history.db"


async def get_checkpointer(db_path: str | None = None) -> AsyncSqliteSaver:
    """Get an AsyncSqliteSaver checkpointer for conversation persistence.

    Args:
        db_path: Path to the SQLite database file. Defaults to data/chat_history.db.

    Returns:
        AsyncSqliteSaver instance.
    """
    path = db_path or str(DEFAULT_DB_PATH)
    return AsyncSqliteSaver.from_conn_string(path)
