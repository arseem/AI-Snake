import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Slider

class VisualizeBoard:

    def __init__(self, engine, interval, colors, map_size, fig_size, control):
        self.control_engine = control
        self.interval = interval
        self.colors = colors
        self.map_size = map_size
        self.fig_size = fig_size

        self.s = engine
        self.last_score = 0
        self.fig, self.ax, self.plot, self.axscores = self.create_board(self.s.map_matrix)
        self.anim = FuncAnimation(self.fig, lambda x: self.update_plot(x, self.plot), interval=self.interval, blit=True)


    def create_board(self, data:np.ndarray):
        fig, ax = plt.subplots(1, 1, figsize=(self.fig_size, self.fig_size))
        fig.canvas.toolbar.pack_forget()
        fig.tight_layout()
        fig.subplots_adjust(left=0, right=1, top=.9, bottom=.1)
        plt.rcParams['keymap.save'].remove('s')
        ax.axis('off')
        
        plot = ax.matshow(data, cmap = ListedColormap(self.colors))
        
        axspeed = plt.axes([0.25, 0.04, 0.55, 0.03])
        self.speed_slider = Slider(ax=axspeed, label='SPEED', valmin=0, valmax=10, valinit=-np.log(self.control_engine.move_interval))
        self.speed_slider.on_changed(self._change_speed)

        axscores = plt.axes([0.1, 0.92, 0.55, 0.1])
        axscores.axis('off')
        axscores.set_figsize = (self.fig_size, self.fig_size//10)

        return fig, ax, plot, axscores


    def _change_speed(self, val):
        self.control_engine.move_interval = np.exp(-val)


    def update_plot(self, _, plot):
        middle_text = False
        high_score_text = self.axscores.text(0, 0.3, s=f"HIGH SCORE: {self.s.high_score}", color=self.colors[1]) 

        if not self.s.is_lost:
            plot.set_data(self.s.map_matrix)

            score_text = self.axscores.text(0, 0, s=f"SCORE:          {self.s.score}", color=self.colors[1])
            self.last_score = self.s.score

        else:
            score_text = self.axscores.text(0, 0, s=f"SCORE:          {self.last_score}", color=self.colors[1])
            middle_text = self.ax.text(self.map_size//2, self.map_size//2, s="YOU LOST\nPRESS SPACEBAR TO RESTART", size=2*self.fig_size, color = self.colors[-2], horizontalalignment='center', verticalalignment='center')

        return [plot, middle_text, score_text, high_score_text] if middle_text else [plot, score_text, high_score_text]


    def run_board(self):
        plt.show()
