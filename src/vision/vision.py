import numpy as np


TAIL = 3
HEAD = 2
APPLE = 1


class Vision:

    def __init__(self, n_of_directions=8):
        if n_of_directions not in (4, 8, 16):
            print('Number of directions must be 4, 8 or 16\nSetting number of directions to 8')
            n_of_directions = 8

        self.n_of_directions = n_of_directions

        self.parts_dict = {'head': HEAD, 'tail': TAIL, 'apple': APPLE}


    def get_distances(self, map_matrix:np.ndarray, head:tuple=()) -> tuple[dict, dict, dict]:
        if not head:
            head = np.argwhere(map_matrix == self.parts_dict['head'])[0][::-1]

        
        size = len(map_matrix)        

        n_wall = head[1]
        s_wall = size - 1 - head[1]
        w_wall = head[0]
        e_wall = size - 1 - head[0]
        nw_wall = 1.4*np.min((n_wall, w_wall))
        ne_wall = 1.4*np.min((n_wall, e_wall))
        sw_wall = 1.4*np.min((s_wall, w_wall))
        se_wall = 1.4*np.min((s_wall, e_wall))

        walls:dict[str:int] = {'n':n_wall, 's':s_wall, 'w':w_wall, 'e':e_wall, 'nw':nw_wall, 'ne':ne_wall, 'sw':sw_wall, 'se':se_wall}
        tails:dict[str:bool] = {'n':False, 's':False, 'w':False, 'e':False, 'nw':False, 'ne':False, 'sw':False, 'se':False}
        apples:dict[str:bool] = {'n':False, 's':False, 'w':False, 'e':False, 'nw':False, 'ne':False, 'sw':False, 'se':False}

        for i in range(size):
            left = head[0]-i if head[0]-i >= 0 else -1
            right = head[0]+i if head[0]+i < size else -1
            up = head[1]-i if head[1]-i >= 0 else -1
            down = head[1]+i if head[1]+i < size else -1

            n = (head[0], up)
            s = (head[0], down)
            w = (left, head[1])
            e = (right, head[1])
            nw = (left, up)
            ne = (right, up)
            sw = (left, down)
            se = (right, down)

            directions:dict[str:tuple] = {'n':n, 's':s, 'w':w, 'e':e, 'nw':nw, 'ne':ne, 'sw':sw, 'se':se}


            for dir, value in zip(directions, directions.values()):
                if not -1 in value:
                    if map_matrix[value[1]][value[0]] == self.parts_dict['tail']:
                        tails[dir] = True

                    if map_matrix[value[1]][value[0]] == self.parts_dict['apple']:
                        apples[dir] = True


        return walls, tails, apples




# test_matrix = np.array(
#     [
#         [3,3,3,0,0,0],
#         [3,0,3,3,3,0],
#         [3,0,0,0,2,0],
#         [3,0,0,0,0,0],
#         [3,0,0,0,0,0],
#         [0,0,0,0,0,1],
#     ]
# )

# v = Vision()
# print(v.get_distances(test_matrix))