from control.manualcontrol import ManualControl
from control.fromsave import FromSave
from control.frommodel import FromModel
from gui.visualizeboard_pg import VisualizeBoard
from engine.snakeengine import SnakeEngine
from vision.vision import Vision
from ai.model import Model
from ai.ga import GA

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


def play_ai_snake():
    snake = SnakeEngine(MAP_SIZE, representations=REPRESENTATIONS)
    vision = Vision(representations=REPRESENTATIONS)
    control = FromModel(snake, MOVE_INTERVAL, vision)
    model = Model(28, 4, [20, 12], 'relu', 'sigmoid', biases=True)
    brain = GA(snake, control, model, N_IN_GENERATION, N_GENERATIONS, populations_path=P_PATH, print_info=False)
    board = VisualizeBoard(snake, FIG_SIZE, control, brain)

    brain.run_generation()
    #brain.t.join()
    board.run_board()


if __name__=='__main__':
    play_ai_snake()