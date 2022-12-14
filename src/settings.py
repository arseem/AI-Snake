from dataclasses import dataclass

@dataclass
class SnakeSettings:
    MAP_SIZE = 25
    INTERVAL = 10
    MOVE_INTERVAL = 0.03
    REPRESENTATIONS = (0, 100, 75, 255)


@dataclass
class GuiSettings:
    FIG_SIZE = 5
    COLORS = ['grey', 'r', 'w', 'g']


@dataclass
class GASettings:
    N_GENERATIONS = 3000
    N_IN_GENERATION = 2000
    POPULATIONS_PATH = './populations/'
    N_PARENTS = False
    VISION_MODE = 'distance'    # 'distance'/'bool'
    NN_ARCHITECTURE = [32, [16], 4]
    HIDDEN_ACTIVATION = 'relu'
    OUTPUT_ACTIVATION = 'sigmoid'

