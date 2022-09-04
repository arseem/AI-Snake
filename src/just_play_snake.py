from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from control.manualcontrol import ManualControl
from control.fromsave import FromSave
from control.frommodel import FromModel
from gui.visualizeboard_pg import VisualizeBoard
from gui.menu import Menu
from engine.snakeengine import SnakeEngine
from vision.vision import Vision
from ai.model import Model
from ai.ga import GA
from saving.saveshandler import SavesHandler
import json

from settings import SnakeSettings, GuiSettings, GASettings

@dataclass
class Setup:
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
    VISION_MODE = GASettings.VISION_MODE
    NN_INPUT = GASettings.NN_ARCHITECTURE[0]
    NN_HIDDEN = GASettings.NN_ARCHITECTURE[1]
    NN_OUTPUT = GASettings.NN_ARCHITECTURE[2]
    NN_HIDDEN_ACTIVATION = GASettings.HIDDEN_ACTIVATION
    NN_OUTPUT_ACTIVATION = GASettings.OUTPUT_ACTIVATION



def play_snake():
    snake = SnakeEngine(Setup.MAP_SIZE, representations=Setup.REPRESENTATIONS, allow_back_move=True)
    key_grabber = ManualControl(snake, Setup.MOVE_INTERVAL)
    board = VisualizeBoard(snake, Setup.FIG_SIZE, key_grabber)

    key_grabber.move()
    board.run_board()


def play_saved_snake():
    save = SavesHandler()

    snake = SnakeEngine(Setup.MAP_SIZE, representations=Setup.REPRESENTATIONS)
    vision = Vision(representations=Setup.REPRESENTATIONS, mode=Setup.VISION_MODE)
    control = FromModel(snake, Setup.MOVE_INTERVAL, vision)
    model = Model(Setup.NN_INPUT, Setup.NN_OUTPUT, Setup.NN_HIDDEN, Setup.NN_HIDDEN_ACTIVATION, Setup.NN_OUTPUT_ACTIVATION, biases=True)
    board = VisualizeBoard(snake, Setup.FIG_SIZE, control)
    weights = ''
    model.model.set_weights(weights)
    control.load_model(model)
    control.move()
    board.run_board()


def play_ai_snake():
    snake = SnakeEngine(Setup.MAP_SIZE, representations=Setup.REPRESENTATIONS)
    vision = Vision(representations=Setup.REPRESENTATIONS, mode=Setup.VISION_MODE)
    control = FromModel(snake, Setup.MOVE_INTERVAL, vision)
    model = Model(Setup.NN_INPUT, Setup.NN_OUTPUT, Setup.NN_HIDDEN, Setup.NN_HIDDEN_ACTIVATION, Setup.NN_OUTPUT_ACTIVATION, biases=True)
    brain = GA(snake, control, model, Setup.N_IN_GENERATION, Setup.N_GENERATIONS, populations_path=Setup.P_PATH, print_info=True)
    board = VisualizeBoard(snake, Setup.FIG_SIZE, control, brain)

    brain.run_generation()
    #brain.t.join()
    board.run_board()


if __name__=='__main__':
    # with open('src/populations/2022_09_02 23_55_04_393604/gen_105.json') as f:
    #     gen = json.load(f)
    #     wei = gen['Individual_9']['Weights']
    #     start = gen['Individual_9']['Starting position']
    #     apples = gen['Individual_9']['Apples']

    #play_saved_snake(wei)

    # play_ai_snake()

    customizable_settings = [Setup.MAP_SIZE, Setup.N_IN_GENERATION, Setup.N_GENERATIONS, Setup.N_PARENTS, Setup.VISION_MODE, Setup.NN_INPUT, Setup.NN_OUTPUT, Setup.NN_HIDDEN, Setup.NN_HIDDEN_ACTIVATION, Setup.NN_OUTPUT_ACTIVATION, Setup.P_PATH]

    while True:
        m = Menu(Setup.FIG_SIZE, customizable_settings)
        checksum, out = m.run_menu()
        for i, n in enumerate(out):
            if '[' in n:
                n = n.replace('[', '').replace(']', '').replace(' ', '')
                n = n.split(',')
                n = [int(a) for a in n]

            elif n == 'False':
                n = False

            else:
                try:
                    n = int(n)
                except ValueError:
                    pass

            out[i] = n

        Setup.MAP_SIZE, Setup.N_IN_GENERATION, Setup.N_GENERATIONS, Setup.N_PARENTS, Setup.VISION_MODE, Setup.NN_INPUT, Setup.NN_OUTPUT, Setup.NN_HIDDEN, Setup.NN_HIDDEN_ACTIVATION, Setup.NN_OUTPUT_ACTIVATION, Setup.P_PATH = out

        if checksum == 1:
            checksum = play_ai_snake()

        elif checksum == 2:
            checksum = play_saved_snake()

        elif checksum == 3:
            checksum = play_snake()

        if checksum == 0:
            break

