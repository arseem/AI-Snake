import numpy as np
import random


class SnakeEngine:

    def __init__(self, map_size:int, apples_list:list=[], starting_points:list=[], high_score:int=0, representations:tuple=(0, 1, 2, 3), max_without_apple=False, allow_back_move=False):
        self._map_size:int = map_size
        self._apples_list = apples_list
        self._starting_points = starting_points

        self._empty_field_rep = representations[0]
        self._apple_rep = representations[1]
        self._head_rep = representations[2]
        self._tail_rep = representations[3]

        self._allow_back_move = allow_back_move

        self.moves_without_apple = 0
        if max_without_apple:
            self.max_without_apple = max_without_apple
        else:
            self.max_without_apple = map_size*5

        self._directions_dict:dict[str:list] = {'U':(0, -1), 'D':(0, 1), 'L':(-1, 0), 'R':(1, 0)}

        self.score = 0
        self.high_score = high_score
        self.is_lost = False
        self.first_move = True

        self._initialize_game()


    def _initialize_game(self):
        self.map_matrix:np.matrix = np.zeros((self._map_size, self._map_size), dtype=int)
        self.moves_without_apple = 0
        self.score = 0

        #   indexes as [x, y]
        if not self._starting_points:
            self._head:list = [random.randint(1, self._map_size-2), random.randint(1, self._map_size-2)]
            self._tail:list[list] = [random.choice([[self._head[0], self._head[1]+1], [self._head[0], self._head[1]-1], [self._head[0]+1, self._head[1]], [self._head[0]-1, self._head[1]]])]

        else:
            self._head = list(self._starting_points[0])
            self._tail = [self._starting_points[1]]

        self._direction:str = 'U' if self._head[1]-self._tail[0][1]==-1 else 'D' if self._head[1]-self._tail[0][1]==1 else 'L' if self._head[0]-self._tail[0][0]==-1 else 'R'
        self._moves = [self._direction]
        self.tail_direction = self._moves[-len(self._tail)]

        self._new_apple()

        self.map_matrix[self._apple[1]][self._apple[0]] = self._apple_rep
        self.map_matrix[self._head[1]][self._head[0]] = self._head_rep
        for i in self._tail:
            self.map_matrix[i[1]][i[0]] = self._tail_rep

    
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
        self.map_matrix[self._head[1]][self._head[0]] = self._tail_rep

        self._tail.append(list(self._head))
        self._head[0] += self._directions_dict[self._direction][0]
        self._head[1] += self._directions_dict[self._direction][1]

        self._moves.append(self._direction)
        self.tail_direction = self._moves[-len(self._tail)]
        
        if self._head == self._apple:
            self._new_apple()
            self.map_matrix[self._apple[1]][self._apple[0]] = self._apple_rep
            self.score += 1
            self.moves_without_apple = 0
            if self.score > self.high_score:
                self.high_score = self.score

        elif (self._head in self._tail) or (self._head[0] in (-1, self._map_size)) or (self._head[1] in (-1, self._map_size)) or self.moves_without_apple==self.max_without_apple:
            self._lost()

        else:
            self.map_matrix[self._tail[0][1]][self._tail[0][0]] = self._empty_field_rep
            self._tail.pop(0)
            self.moves_without_apple += 1

        
        if not self.is_lost:
            self.map_matrix[self._head[1]][self._head[0]] = self._head_rep


    def _lost(self):
        self.is_lost = True
        self._initialize_game()

    
    def make_move(self, direction:str):
        self.is_lost = False

        if direction not in self._directions_dict.keys():
            raise Exception('Wrong direction indicator')

        if self._allow_back_move:
            if {direction, self._direction} in [{'U', 'D'}, {'R', 'L'}]:
                direction = self._direction

        self._direction = direction
        self._tick()
        