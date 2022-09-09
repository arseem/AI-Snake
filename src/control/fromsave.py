import threading

class FromSave:

    def __init__(self, engine, move_interval, save):
        self.s = engine
        self.move_interval = move_interval
        self.save = save
        self.gen_num = 1
        self.ind_num = 1
        self.gen_num_set = 1
        self.ind_num_set = 1
        self.highest_fitness = (0, 0)
        self.n_gen = save.n_of_gens
        self.loop = False
        self.pause = False
        self.t = threading.Timer(self.move_interval, self.move)

        self.current_loaded_gen_num = False

        self.load_individual()

    def load_individual(self):
        if not self.gen_num==self.gen_num_set:
            self.gen_num = self.gen_num_set
        elif not self.loop:
            self.gen_num+=1
            self.gen_num_set+=1
        if not self.ind_num==self.ind_num_set:
            self.ind_num = self.ind_num_set

        if self.current_loaded_gen_num!=self.gen_num:
            self.current_loaded_gen = self.save.import_generation(self.gen_num)
            self.current_loaded_gen_num = self.gen_num

        self.n_in_gen = len(self.current_loaded_gen[1].columns)
        self.current_ind = self.current_loaded_gen[1].iloc[:, self.ind_num-1]
        self.highest_fitness_gen = self.current_loaded_gen[0]
        self.highest_fitness = (self.highest_fitness_gen, self.gen_num) if self.highest_fitness_gen>=self.highest_fitness[0] else self.highest_fitness
        self.moves = list(self.current_ind['Moves'][1])
        self.last_fitness = self.current_ind['Fitness']
        self.input_neurons = self.current_ind['Input neurons data']
        self.data_check = self.input_neurons[0][0]
        self.s._starting_points = self.current_ind['Starting position']
        self.s._apples_list = self.current_ind['Apples']
        self.s._initialize_game()
        self.s.is_lost = 0
        if not self.t.is_alive():
            self.move()

        
    def move(self):
        t = threading.Timer(self.move_interval, self.move)
        t.daemon = True
        t.start()
        self.t = t
        if not self.pause:
            if not self.s.is_lost and self.moves:
                self.s.make_move(self.moves.pop(0))
                self.data_check = self.input_neurons.pop(0)[0]
            
            else:
                t.cancel()
                self.load_individual()
