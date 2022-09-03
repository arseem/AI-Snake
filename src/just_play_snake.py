from control.manualcontrol import ManualControl
from control.fromsave import FromSave
from control.frommodel import FromModel
from gui.visualizeboard_pg import VisualizeBoard
from engine.snakeengine import SnakeEngine
from vision.vision import Vision
from ai.model import Model
from ai.ga import GA
import json

from settings import SnakeSettings, GuiSettings, GASettings

MAP_SIZE = SnakeSettings.MAP_SIZE
FIG_SIZE = GuiSettings.FIG_SIZE
COLORS = GuiSettings.COLORS
MAP_SIZE = SnakeSettings.MAP_SIZE
INTERVAL = SnakeSettings.INTERVAL
MOVE_INTERVAL = SnakeSettings.MOVE_INTERVAL
REPRESENTATIONS = SnakeSettings.REPRESENTATIONS
N_IN_GENERATION = GASettings.N_IN_GENERATION
N_GENERATIONS = GASettings.N_GENERATIONS
N_PARENTS = GASettings.N_PARENTS
P_PATH = GASettings.POPULATIONS_PATH


def play_snake():
    snake = SnakeEngine(MAP_SIZE, representations=REPRESENTATIONS)
    key_grabber = ManualControl(snake, MOVE_INTERVAL)
    board = VisualizeBoard(snake, FIG_SIZE, key_grabber)

    key_grabber.move()
    board.run_board()


def play_saved_snake(weights, start_pos=False, apples=False):
    snake = SnakeEngine(MAP_SIZE, representations=REPRESENTATIONS)
    vision = Vision(representations=REPRESENTATIONS, mode='distance')
    control = FromModel(snake, MOVE_INTERVAL, vision)
    model = Model(32, 4, [16, 16], 'relu', 'sigmoid', biases=True)
    board = VisualizeBoard(snake, FIG_SIZE, control)

    import numpy as np
    aaa = []
    for i in weights:
        for j in i:
            j = np.array(j)
        i = np.array(i)
        aaa.append(i)
    model.model.set_weights(np.array(aaa))
    control.load_model(model)
    control.move()
    board.run_board()


def play_ai_snake():
    snake = SnakeEngine(MAP_SIZE, representations=REPRESENTATIONS)
    vision = Vision(representations=REPRESENTATIONS, mode='distance')
    control = FromModel(snake, MOVE_INTERVAL, vision)
    model = Model(32, 4, [16], 'relu', 'sigmoid', biases=True)
    brain = GA(snake, control, model, N_IN_GENERATION, N_GENERATIONS, populations_path=P_PATH, print_info=True)
    board = VisualizeBoard(snake, FIG_SIZE, control, brain)

    brain.run_generation()
    #brain.t.join()
    board.run_board()


if __name__=='__main__':
    # with open('src/populations/2022_09_01 16_19_33_902535/gen_74.json') as f:
    #     gen = json.load(f)
    #     wei = gen['Individual_8']['Weights']
    #     start = gen['Individual_8']['Starting position']
    #     apples = gen['Individual_8']['Apples']

    # play_saved_snake(wei)

    play_ai_snake()
