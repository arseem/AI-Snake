from control.manualcontrol import ManualControl
from gui.visualizeboard import VisualizeBoard
from engine.snakeengine import SnakeEngine

from settings import SnakeSettings

MAP_SIZE = SnakeSettings.MAP_SIZE


if __name__=='__main__':
    snake = SnakeEngine(MAP_SIZE)
    board = VisualizeBoard(snake)
    key_grabber = ManualControl(snake)

    key_grabber.move()
    board.run_board()