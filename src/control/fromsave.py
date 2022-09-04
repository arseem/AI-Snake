import threading
import multiprocessing

class FromSave:

    def __init__(self, engine, move_interval, save):
        self.s = engine
        self.move_interval = move_interval
        self.save = save
        self.gen_num = 1
        self.ind_num = 1

        self.load_individual()

    def load_individual(self):
        #self.t.cancel()
        self.current_ind = self.save.import_generation(self.gen_num)[1].iloc[:, self.ind_num-1]
        self.moves = list(self.current_ind['Moves'][1])
        self.s._starting_points = self.current_ind['Starting position']
        self.s._apples_list = self.current_ind['Apples']
        self.s._initialize_game()
        self.s.is_lost = 0
        self.move()

        
    def move(self):
        t = threading.Timer(self.move_interval, self.move)
        t.daemon = True
        t.start()
        if not self.s.is_lost and self.moves:
            self.s.make_move(self.moves.pop(0))
        
        else:
            t.cancel()
            self.gen_num+=1
            self.load_individual()
