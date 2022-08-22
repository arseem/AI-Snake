from dataclasses import dataclass

@dataclass
class SnakeSettings:
    MAP_SIZE = 40
    INTERVAL = 10
    MOVE_INTERVAL = 0.05
    REPRESENTATIONS = (0, 100, 75, 255)
    
@dataclass
class GuiSettings:
    FIG_SIZE = 7
    COLORS = ['grey', 'r', 'w', 'g']


@dataclass
class GASettings:
    N_GENERATIONS = 300
    N_IN_GENERATION = 2
    POPULATIONS_PATH = './populations/'
    N_PARENTS = False

