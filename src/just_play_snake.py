from dataclasses import dataclass
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


def play_ai_snake():
    snake = SnakeEngine(Setup.MAP_SIZE, representations=Setup.REPRESENTATIONS)
    vision = Vision(representations=Setup.REPRESENTATIONS, mode=Setup.VISION_MODE)
    control = FromModel(snake, Setup.MOVE_INTERVAL, vision)
    model = Model(Setup.NN_INPUT, Setup.NN_OUTPUT, Setup.NN_HIDDEN, Setup.NN_HIDDEN_ACTIVATION, Setup.NN_OUTPUT_ACTIVATION, biases=True)
    brain = GA(snake, control, model, Setup.N_IN_GENERATION, Setup.N_GENERATIONS, populations_path=Setup.P_PATH, print_info=True)
    board = VisualizeBoard(snake, Setup.FIG_SIZE, control, brain=brain)

    brain.run_generation()
    #brain.t.join()
    return(board.run_board())


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

        if checksum == 0:
            break

if __name__=='__main__':
    main()

