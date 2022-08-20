from control.manualcontrol import ManualControl
from control.fromsave import FromSave
from control.frommodel import FromModel
from gui.visualizeboard_pg import VisualizeBoard
from engine.snakeengine import SnakeEngine
from vision.vision import Vision
from ai.model import Model

from settings import SnakeSettings, GuiSettings

MAP_SIZE = SnakeSettings.MAP_SIZE
FIG_SIZE = GuiSettings.FIG_SIZE
COLORS = GuiSettings.COLORS
MAP_SIZE = SnakeSettings.MAP_SIZE
INTERVAL = SnakeSettings.INTERVAL
MOVE_INTERVAL = SnakeSettings.MOVE_INTERVAL
REPRESENTATIONS = SnakeSettings.REPRESENTATIONS


def play_snake():
    snake = SnakeEngine(MAP_SIZE, representations=REPRESENTATIONS)
    key_grabber = ManualControl(snake, MOVE_INTERVAL)
    board = VisualizeBoard(snake, FIG_SIZE, key_grabber)

    key_grabber.move()
    board.run_board()


if __name__=='__main__':
    play_snake()