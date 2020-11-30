from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid


class DiffKind(Enum):
    ADD = "add"
    CHANGE = "change"
    DELETE = "delete"


@dataclass
class Diff:
    id: str
    kind: DiffKind
    file: str
    diff: Optional[str]


@dataclass
class Revision:
    message: str
    diffs: List[Diff]
    id: str = uuid.uuid4().hex
    timestamp: datetime = datetime.now()


@dataclass
class Branch:
    name: str
    revisions: List[Revision]
    source: Dict[str, Revision]


@dataclass
class Tag:
    revision: Revision
    name: str
    message: str
