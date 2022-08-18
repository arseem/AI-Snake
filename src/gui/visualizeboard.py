import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap

from settings import GuiSettings, SnakeSettings

FIG_SIZE = GuiSettings.FIG_SIZE
COLORS = GuiSettings.COLORS
MAP_SIZE = SnakeSettings.MAP_SIZE
INTERVAL = SnakeSettings.INTERVAL


class VisualizeBoard:

    def __init__(self, engine):

        self.s = engine
        self.fig, self.ax, self.plot = self.create_board(self.s.map_matrix)
        self.anim = FuncAnimation(self.fig, lambda x: self.update_plot(x, self.plot), interval = INTERVAL, blit = True)

    def create_board(self, data:np.ndarray):
        fig, ax = plt.subplots(1, 1, figsize=(FIG_SIZE,FIG_SIZE))
        fig.canvas.toolbar.pack_forget()
        fig.subplots_adjust(0,0,1,1)
        plt.rcParams['keymap.save'].remove('s')
        plt.axis('off')
        plt.grid()
        plot = ax.matshow(data, cmap = ListedColormap(COLORS))

        return fig, ax, plot


    def update_plot(self, _, plot):
        if not self.s.is_lost:
            plot.set_data(self.s.map_matrix)

        else:
            plt.text(MAP_SIZE//2, MAP_SIZE//2, s="YOU LOST\nPRESS SPACEBAR TO RESTART", size=2*FIG_SIZE, color = COLORS[-2], horizontalalignment='center', verticalalignment='center')
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        return [plot]

    def run_board(self):
        plt.show()
