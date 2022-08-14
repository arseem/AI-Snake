import numpy as np
import random

MAP_SIZE = 50


class Snake:

    def __init__(self, map_size:int):
        self._map_size:int = map_size

        self._directions_dict:dict[str:list] = {'U':[0, -1], 'D':[0, 1], 'L':[-1, 0], 'R':[1, 0]}

        self._initalize_game()


    def _initalize_game(self):
        self.map_matrix:np.matrix = np.matrix(np.zeros((self._map_size, self._map_size)), dtype=int)

        #   0 - empty field
        #   1 - _apple
        #   2 - snake's head
        #   3 - snake's tail

        #   indexes as [x, y]

        self._head:list = [random.randint(1, self._map_size-1), random.randint(1, self._map_size-1)]
        self._tail:list[list] = [[random.choice([[self._head[0], self._head[1]+1], [self._head[0], self._head[1]-1], [self._head[0]+1, self._head[1]], [self._head[0]-1, self._head[1]]])]]

        self.direction:str = 'U' if self._head[0]-self._tail[0][0]==-1 else 'D' if self._head[0]-self._tail[0][0]==1 else 'L' if self._head[1]-self._tail[0][1]==-1 else 'R'

        self._new_apple()

        self.map_matrix[self._apple[1]][self._apple[0]] = 1
        self.map_matrix[self._head[1]][self._head[0]] = 2
        for i in self._tail:
            self.map_matrix[i[1]][i[0]] = 3

        self._tick()

    
    def _new_apple(self):
        self._apple:list = [random.randint(1, self._map_size-1), random.randint(1, self._map_size-1)]

        while self._apple==self._head or self._apple in self._tail:
            self._apple = [random.randint(1, self._map_size-1), random.randint(1, self._map_size-1)]

    
    def _tick(self):
        self._tail.append(self._head)
        self._head[0] += self.directions_dict[self.directions_dict][0]
        self._head[1] += self.directions_dict[self.directions_dict][1]

        if self._head == self._apple:
            self._new_apple()

        else:
            self._tail.pop(0)


    def print_map(self):
        for i in self.map_matrix:
            for j in self.map_matrix:
                print(j, end='')
            
            print(' ')