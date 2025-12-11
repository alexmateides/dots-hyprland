from enum import Enum

class SelectOutcome(Enum):
    EXIT = 0
    REFRESH = 1
    RETURN = 2
    SUBMENU = 3
    WAIT = 4