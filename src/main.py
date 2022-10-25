from dataclasses import dataclass
import json
import numpy as np

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
    snake = SnakeEngine(Setup.MAP_SIZE, representations=Setup.REPRESENTATIONS, allow_back_move=True, max_without_apple=10**10)
    key_grabber = ManualControl(snake, Setup.MOVE_INTERVAL)
    board = VisualizeBoard(snake, Setup.FIG_SIZE, key_grabber)

    key_grabber.move()
    return(board.run_board())


def play_saved_snake():
    save = SavesHandler()

    snake = SnakeEngine(Setup.MAP_SIZE, representations=Setup.REPRESENTATIONS)
    control = FromSave(snake, Setup.MOVE_INTERVAL, save)
    
    board = VisualizeBoard(snake, Setup.FIG_SIZE, control, brain=control)
    return(board.run_board())


def play_ai_snake(init_weights=False, name=False, previous_path=False):
    snake = SnakeEngine(Setup.MAP_SIZE, representations=Setup.REPRESENTATIONS, max_without_apple=2500)
    vision = Vision(representations=Setup.REPRESENTATIONS, mode=Setup.VISION_MODE)
    control = FromModel(snake, Setup.MOVE_INTERVAL, vision)
    model = Model(Setup.NN_INPUT, Setup.NN_OUTPUT, Setup.NN_HIDDEN, Setup.NN_HIDDEN_ACTIVATION, Setup.NN_OUTPUT_ACTIVATION, biases=True)
    brain = GA(snake, control, model, Setup.N_IN_GENERATION, Setup.N_GENERATIONS, populations_path=Setup.P_PATH, print_info=True, parallel=False, init_weights=init_weights, population_name=name, previous_path=previous_path)
    board = VisualizeBoard(snake, Setup.FIG_SIZE, control, brain=brain)

    brain.run_generation()
    #brain.t.join()
    return(board.run_board())


def resume_ai_snake():
    save = SavesHandler()
    (_, _, Setup.N_IN_GENERATION, Setup.N_PARENTS, _, Setup.VISION_MODE, nn_architecture) = save.info_dict.values()
    Setup.NN_INPUT = nn_architecture[0][0]
    Setup.NN_HIDDEN = nn_architecture[0][1][0]
    Setup.NN_HIDDEN_ACTIVATION = nn_architecture[0][1][1]
    Setup.NN_OUTPUT = nn_architecture[0][2][0]
    Setup.NN_OUTPUT_ACTIVATION = nn_architecture[0][2][1]

    with open(f'{save.path}/models/last_gen_all_models.json') as f:
        weights = list(json.loads(f.read()).values())
    
    for i, w in enumerate(weights):
        for j, k in enumerate(w):
            weights[i][j] = np.asarray(k, dtype=float)

    new_name = f"{save.path.split('/')[-1]}_RESUMED"
    new_path = f"{save.path[-len(save.path.split('/')[-1])]}/{new_name}"

    play_ai_snake(init_weights=weights, name=new_name, previous_path=save.path)


def main():
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

        elif checksum == 4:
            checksum = resume_ai_snake()

        if checksum == 0:
            break

if __name__=='__main__':
    main()

