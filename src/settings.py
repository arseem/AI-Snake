from dataclasses import dataclass

@dataclass
class SnakeSettings:
    MAP_SIZE = 25
    INTERVAL = 10
    MOVE_INTERVAL = 0.05
    REPRESENTATIONS = (0, 100, 254, 255)
    
@dataclass
class GuiSettings:
    FIG_SIZE = 5
    COLORS = ['grey', 'r', 'w', 'g']


@dataclass
class GASettings:
    N_GENERATIONS = 300
    N_IN_GENERATION = 200
    POPULATIONS_PATH = './populations/'
    N_PARENTS = 10

