"""In-process conversation checkpointer for the customer service agent.

This module wraps LangGraph's :class:`InMemorySaver` behind a singleton
accessor. Conversation history lives only for the lifetime of the current
process; swap in :class:`langgraph.checkpoint.sqlite.SqliteSaver` (or its
async equivalent) for cross-restart persistence.
"""

from langgraph.checkpoint.memory import InMemorySaver


_checkpointer: InMemorySaver | None = None


def get_checkpointer() -> InMemorySaver:
    """Return the process-wide :class:`InMemorySaver` singleton.

    Returns:
        The shared :class:`InMemorySaver` instance.
    """
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = InMemorySaver()
    return _checkpointer


def reset_checkpointer() -> None:
    """Drop the singleton so the next ``get_checkpointer`` call rebuilds it.

    Intended for tests that need a clean conversation store.
    """
    global _checkpointer
    _checkpointer = None
