from enum import Enum


class RunStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ChangeType(str, Enum):
    NEW = "NEW"
    UPDATED = "UPDATED"
    CLOSED = "CLOSED"
    DEADLINE_CHANGED = "DEADLINE_CHANGED"


class UserPostingStatus(str, Enum):
    PENDENT = "pendent"
    REVISADA = "revisada"
    INTERESSA = "interessa"
    DESCARTADA = "descartada"
    APLICADA = "aplicada"
