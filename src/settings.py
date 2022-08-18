from dataclasses import dataclass

@dataclass
class SnakeSettings:
    MAP_SIZE = 25
    INTERVAL = 10
    MOVE_INTERVAL = 0.07

@dataclass
class GuiSettings:
    FIG_SIZE = 5
    COLORS = ['k', 'r', 'w', 'g']

@dataclass
class VisionSettings:
    TAIL = 3
    HEAD = 2
    APPLE = 1

