from dataclasses import dataclass
from typing import Any


@dataclass
class AgentContext:
    user: Any
    session_id: str = ""
    user_query: str = ""