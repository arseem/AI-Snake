from turtle import up
import numpy as np
import random

MAP_SIZE = 25


class SnakeEngine:

    def __init__(self, map_size:int, apples_list:list=[], starting_points=[]):
        self._map_size:int = map_size
        self._apples_list = apples_list
        self._starting_points = starting_points

        self._directions_dict:dict[str:list] = {'U':(0, -1), 'D':(0, 1), 'L':(-1, 0), 'R':(1, 0)}

        self.is_lost = False

        self._initalize_game()


    def _initalize_game(self):
        self.map_matrix:np.matrix = np.zeros((self._map_size, self._map_size), dtype=int)

        #   0 - empty field
        #   1 - apple
        #   2 - snake's head
        #   3 - snake's tail

        #   indexes as [x, y]
        if not self._starting_points:
            self._head:list = [random.randint(1, self._map_size-2), random.randint(1, self._map_size-2)]
            self._tail:list[list] = [random.choice([[self._head[0], self._head[1]+1], [self._head[0], self._head[1]-1], [self._head[0]+1, self._head[1]], [self._head[0]-1, self._head[1]]])]

        else:
            self._head = self._starting_points[0]
            self._tail = [self._starting_points[1]]

        self._direction:str = 'U' if self._head[1]-self._tail[0][1]==-1 else 'D' if self._head[1]-self._tail[0][1]==1 else 'L' if self._head[0]-self._tail[0][0]==-1 else 'R'

        self._new_apple()

        self.map_matrix[self._apple[1]][self._apple[0]] = 1
        self.map_matrix[self._head[1]][self._head[0]] = 2
        for i in self._tail:
            self.map_matrix[i[1]][i[0]] = 3

    
    def _new_apple(self):
        if not self._apples_list:
            self._apple:list = [random.randint(1, self._map_size-1), random.randint(1, self._map_size-1)]

            while self._apple==self._head or self._apple in self._tail:
                self._apple = [random.randint(1, self._map_size-1), random.randint(1, self._map_size-1)]

        else:
            self._apple = self._apples_list.pop(0)
            
            if self._apple==self._head or self._apple in self._tail:
                raise Exception('Wrong apple indexes')

    
    def _tick(self):
        self.map_matrix[self._head[1]][self._head[0]] = 3

        self._tail.append(list(self._head))
        self._head[0] += self._directions_dict[self._direction][0]
        self._head[1] += self._directions_dict[self._direction][1]
        
        if self._head == self._apple:
            self._new_apple()
            self.map_matrix[self._apple[1]][self._apple[0]] = 1

        elif (self._head in self._tail) or (self._head[0] in (-1, self._map_size)) or (self._head[1] in (-1, self._map_size)):
            self._lost()

        else:
            self.map_matrix[self._tail[0][1]][self._tail[0][0]] = 0
            self._tail.pop(0)

        
        if not self.is_lost:
            self.map_matrix[self._head[1]][self._head[0]] = 2


    def _lost(self):
        self.is_lost = True
        self._initalize_game()

    
    def make_move(self, direction:str):
        self.is_lost = False

        if direction not in self._directions_dict.keys():
            raise Exception('Wrong direction indicator')

        if {direction, self._direction} in [{'U', 'D'}, {'R', 'L'}]:
            direction = self._direction

        self._direction = direction
        self._tick()



if __name__=='__main__':
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from matplotlib.colors import ListedColormap
    import threading
    import keyboard

    FIG_SIZE = 5
    COLORS = ['k', 'r', 'w', 'g']

    def update_plot(_):
        global current_direction
        with LOCK:
            c_dir = current_direction  

        if c_dir:
            s.make_move(c_dir)

        if not s.is_lost:
            plot.set_data(s.map_matrix)

        else:
            plt.text(MAP_SIZE//2, MAP_SIZE//2, s="YOU LOST\nPRESS SPACEBAR TO RESTART", size=2*FIG_SIZE, color = COLORS[-2], horizontalalignment='center', verticalalignment='center')
            fig.canvas.draw()
            fig.canvas.flush_events()
            while True:
                press = keyboard.read_key()
                if press == 'space':
                    with LOCK:
                        current_direction = None
                        
                    plot.set_data(s.map_matrix)
                    s.is_lost = False
                    break

        return [plot]

    def get_direction():
        global current_direction
        while True:
            if not s.is_lost:
                press = keyboard.read_key()
                try:  
                    if press == 'w':
                        with LOCK:
                            current_direction = 'U'
                    if press == 's':
                        with LOCK:
                            current_direction = 'D'
                    if press == 'a':
                        with LOCK:
                            current_direction = 'L'
                    if press == 'd':
                        with LOCK:
                            current_direction = 'R'
                except:
                    pass


    LOCK = threading.Lock()

    s = SnakeEngine(MAP_SIZE)
    current_direction = None

    detect_key = threading.Thread(target=get_direction, daemon=True)
    detect_key.start()

    fig, ax = plt.subplots(1, 1, figsize=(FIG_SIZE,FIG_SIZE))
    fig.canvas.toolbar.pack_forget()
    fig.subplots_adjust(0,0,1,1)
    plt.rcParams['keymap.save'].remove('s')
    plt.axis('off')
    plt.grid()
    plot = ax.matshow(s.map_matrix, cmap = ListedColormap(COLORS))

    anim = FuncAnimation(fig, update_plot, interval = 10, blit = True)
    plt.show()