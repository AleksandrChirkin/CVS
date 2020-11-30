from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class DiffKind(Enum):
    ADD = "add"
    CHANGE = "change"
    DELETE = "delete"


@dataclass
class Diff:
    diff: Optional[str]
    file: str
    id: str
    kind: DiffKind


@dataclass
class Revision:
    diffs: List[Diff]
    id: str
    message: str
    timestamp: datetime


@dataclass
class Branch:
    name: str
    revisions: List[Revision]
    source: Dict[str, Revision]
