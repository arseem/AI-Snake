import keras
import datetime
import json
import pandas as pd
import numpy as np
import threading
import os
import random
import time
from copy import deepcopy


class GA():

    def __init__(self, engine, control_engine, model, n_in_generation:int, n_generation:int, n_parents=False, mutation_factor=2, fast_mode=False, prevent_loops=True, populations_path='./!POPULATIONS/', auto_change_map_size=False, print_info=True):
        self.n_in_gen = n_in_generation
        self.n_gen = n_generation

        self.path = populations_path
        
        self.t = threading.Thread(target=self._run_generation, daemon=True)

        self.n_parents = n_parents if n_parents else self._compute_n_parents()

        self.mutation_factor = mutation_factor
        self._prevent_loops = prevent_loops
        self.data_check = ''
        self.dir_to_go = ''
        self.time_delay = 0
        self.s = engine
        self.given_map_size = self.s._map_size
        self.auto_map = auto_change_map_size
        self.print_info = print_info
        if auto_change_map_size:
            self.s._map_size = 4
            self.s._initialize_game()
        self.control_engine = control_engine
        if fast_mode:
            self.control_engine.move_interval = 0
        self.model = model
        self.n_nodes_hidden = model.n_nodes_hidden
        self.n_nodes_output = model.n_nodes_output
        self.info = ''
        self.pause = False
        self.population = self._init_population()


    def _compute_n_parents(self):
        n=0
        while n+(2+(n-1))*n < self.n_in_gen:
            n+=1
        
        return n//2


    def _init_population(self):
        self.gen_num = 0
        self.ind_num = 0
        self.last_fitness = 0
        self.highest_fitness = (0, '-')
        self.highest_fitness_gen = 0
        self.highest_fitness_gen_score = 0
        self.add_to_map = 2
        population = []
        self.timestamp = str(datetime.datetime.now())
        self.folder = self.timestamp.replace(':', '_').replace('.', '_').replace('-', '_')
        os.makedirs(f'{self.path}{self.folder}') 
        info_dict = {
            'Timestamp': self.timestamp,
            'Number of generations':self.n_gen,
            'Individuals in generation': self.n_in_gen,
            'Number of parents': self.n_parents,
            'Mutation factor': self.mutation_factor,
            'Vision mode': self.control_engine.vision_engine.mode,
            'Neural Network architecture': [[self.model.n_nodes_input, (tuple([n for n in self.model.n_nodes_hidden]), self.model.hidden_activation), (self.model.n_nodes_output, self.model.output_activation)]]
        }

        with open(f'{self.path}{self.folder}/info.json', 'w') as f:
            info = pd.DataFrame(data=info_dict.values(), index=info_dict.keys(), columns=['POPULATION INFO'])
            print(info)
            info.to_json(f, orient='columns', indent=4)

        for _ in range(self.n_in_gen):
            subject = keras.models.clone_model(self.model.model)
            population.append(subject)
        
        return population

    
    def _calc_fitness(self, score, n_moves):
        #return 1000*(score**10)/(n_moves/score) if score!=0 else 1/n_moves
        #return round(n_moves+((2**score)+(score**2.1)*500) - ((score**1.2)*((0.25*n_moves)**1.3)))
        #return score**10/(n_moves/score) if score else n_moves
        #return 1000*score + n_moves
        return n_moves*n_moves*(2**score)

    
    def _run_generation(self):
        start_gen_timer = time.perf_counter()
        self.gen_num += 1
        gen = -1
        self.ind_num = 0
        self.highest_fitness_gen = 0

        gen_dict = {
            'Index': [],
            'Fitness': [],
            'Score': [],
            'Starting position': [],
            'Apples': [],
            'Moves': [],
            'Input neurons data': [],
            'Weights': []
        }

        with open(f'{self.path}{self.folder}/gen_{self.gen_num}.json', 'a') as f:
            f.write('{\n\n')
            add = ''

            for i, model in enumerate(self.population):
                
                start_ind_timer = time.perf_counter()
                self.ind_num += 1
                self.model.model = model
                self.control_engine.load_model(self.model)
                moves = ''
                input_data = []
                starting_pos = (tuple(self.s._head), tuple(self.s._tail[0]))
                apples = []
                apples.append(tuple(self.s._apple))
                last_score = 0
                data_history = []
                
                while not self.s.is_lost:

                    while self.pause:
                        pass
                    
                    one_move = time.perf_counter()
                    move, data = self.control_engine._move_for_learning()
                    self.data_check = list(data[0])
                    self.dir_to_go = move
                    if self._prevent_loops:
                        if self.data_check in data_history and self.s.score==last_score:
                            self.s.is_lost = True
                            print('LOOPED')
                        data_history.append(self.data_check)
                    moves+=move
                    input_data.append(data)
                    #print(data)

                    if self.s.score != last_score:
                        data_history = []
                        apples.append(self.s._apple)
                        last_score+=1

                    while time.perf_counter() - one_move < self.time_delay:
                        a = 0
                        a += 1

                    #print(round(time.perf_counter() - one_move, 4))

                #turns = set(list(moves))
                fit = self._calc_fitness(last_score, len(moves))
                self.last_fitness = fit
                if fit > self.highest_fitness_gen:
                    self.highest_fitness_gen = fit
                    self.highest_fitness_gen_score = last_score
                if fit > self.highest_fitness[0]:
                    self.highest_fitness = (fit, self.gen_num)

                gen_dict['Index'].append(i)
                gen_dict['Fitness'].append(fit)
                gen_dict['Score'].append(last_score)
                gen_dict['Moves'].append((len(moves), moves))
                gen_dict['Starting position'].append(starting_pos)
                gen_dict['Apples'].append(apples)
                gen_dict['Input neurons data'].append(input_data)
                gen_dict['Weights'].append(self.model.model.get_weights())

                gen = pd.DataFrame(data=gen_dict.values(), index=gen_dict.keys(), columns=[f'Individual_{n}' for n in gen_dict['Index']])
                gen_to_write = gen[[f'Individual_{i}']]

                f.write(f'{add}' + gen_to_write.to_json(orient='columns')[1:-1])
                
                add = ',\n\n'

                #if self.print_info:
                    #print(f'Gen {self.gen_num}\t|\tIndividual {i+1}/{self.n_in_gen}\t|\tScore: {last_score}\t|\tFitness: {fit}\t|\tTime: {round(time.perf_counter()-start_ind_timer,2)}')

                self.s.is_lost = False
            
            f.write('\n\n}')

        fitness_sum = gen.loc['Fitness'].sum()
        choice_weights = [(gen[individual].loc['Fitness']**10)/fitness_sum for individual in gen]
        all_indexes = list(range(self.n_in_gen))
        parents_indexes = []
        for _ in range(self.n_parents):
            new_offspring = random.choices(all_indexes, weights=choice_weights)[0]
            parents_indexes.append(new_offspring)
            choice_weights.pop(all_indexes.index(new_offspring))
            all_indexes.remove(new_offspring)

        parents = gen.iloc[:, parents_indexes]

        self._crossover(parents)

        if self.gen_num%5==0 and self.s._map_size < self.given_map_size and self.auto_map:
            self.s._map_size += self.add_to_map
            self.s._initialize_game()
            self.add_to_map += 1

        while self.s._map_size > self.given_map_size and self.auto_map:
            self.s._map_size -= 1
            self.s._initialize_game()

        if self.print_info:
            print(f'\nGeneration {self.gen_num}: Finished\t|\tTime: {round(time.perf_counter()-start_gen_timer, 2)}s')
            print("PARENTS:")
            print(parents.loc[['Index', 'Fitness', 'Score', 'Moves']])

        if not self.gen_num>=self.n_gen:
            self._run_generation()


    def _crossover(self, parents):
        parents_weights = [parents[individual].loc['Weights'] for individual in parents]
        parents_weights_copy = deepcopy(parents_weights)
        offspring = []

        for i, parent1 in enumerate(parents_weights):
            if i!=len(parents_weights)-1:
                for _, parent2, in enumerate(parents_weights[i+1:]):
                    # new_offspring_1 = [[] for _ in range(len(parent1))]
                    # new_offspring_2 = [[] for _ in range(len(parent1))]
                    # new_offspring_1 = []
                    # new_offspring_2 = []

                    # for layer1, layer2 in zip(parent1, parent2):
                    #     new_layer_1 = []
                    #     new_layer_2 = []

                        # TYP 3
                        # if layer1.ndim == 2:

                        #     for l1, l2 in zip(layer1, layer2):
                        #         new_sublayer_1 = []
                        #         new_sublayer_2 = []
                        #         for i in range(len(l1)):
                        #             if i%2==0:
                        #                 new_sublayer_1.append(l1[i] if random.uniform(0, 1) > self.mutation_factor/(self.n_parents*10) else random.uniform(-1, 1))
                        #                 new_sublayer_2.append(l2[i] if random.uniform(0, 1) > self.mutation_factor/(self.n_parents*10) else random.uniform(-1, 1))
                        #             else:
                        #                 new_sublayer_1.append(l2[i] if random.uniform(0, 1) > self.mutation_factor/(self.n_parents*10) else random.uniform(-1, 1))
                        #                 new_sublayer_2.append(l1[i] if random.uniform(0, 1) > self.mutation_factor/(self.n_parents*10) else random.uniform(-1, 1))

                        #         new_layer_1.append(np.array(new_sublayer_1))
                        #         new_layer_2.append(np.array(new_sublayer_2))
                        
                        # else:
                        #     for i in range(len(layer1)):
                        #         if i%2==0:
                        #             new_layer_1.append(layer1[i] if random.uniform(0, 1) > self.mutation_factor/(self.n_parents*10) else random.uniform(-1, 1))
                        #             new_layer_2.append(layer2[i] if random.uniform(0, 1) > self.mutation_factor/(self.n_parents*10) else random.uniform(-1, 1))
                        #         else:
                        #             new_layer_1.append(layer2[i] if random.uniform(0, 1) > self.mutation_factor/(self.n_parents*10) else random.uniform(-1, 1))
                        #             new_layer_2.append(layer1[i] if random.uniform(0, 1) > self.mutation_factor/(self.n_parents*10) else random.uniform(-1, 1))


                        # new_offspring_1.append(np.array(new_layer_1))
                        # new_offspring_2.append(np.array(new_layer_2))

                        # TYP 1
                        # pivot = random.randint(1, len(layer1)-1)
                        # temp1 = deepcopy(layer2[:pivot])
                        # temp2 = deepcopy(layer1[:pivot])
                        # new_layer_1 = deepcopy(layer1)
                        # new_layer_2 = deepcopy(layer2)
                        # new_layer_1[:pivot] = temp1
                        # new_layer_2[:pivot] = temp2
                        # for l in range(len(new_layer_1)):
                        #     for _ in range(self.mutation_factor):
                        #         if new_layer_1.ndim>=2:
                        #             new_layer_1[l][random.randint(0, len(new_layer_1[l])-1)] = random.uniform(-1, 1)
                        #             new_layer_2[l][random.randint(0, len(new_layer_1[l])-1)] = random.uniform(-1, 1)

                        # new_offspring_1.append(new_layer_1)
                        # new_offspring_2.append(new_layer_2)
                    
                    # TYP 2
                    # for j in range(0, len(parent1), 2):
                    #     new_offspring_1[j] = parent1[j]
                    #     new_offspring_1[j+1] = parent2[j+1]
                    #     new_offspring_2[j] = parent2[j]
                    #     new_offspring_2[j+1] = parent1[j+1]

                    #     for _ in range(self.mutation_factor):
                    #         new_offspring_1[j][random.randint(0, len(new_offspring_1[j])-1)] = random.uniform(-1, 1)
                    #         new_offspring_2[j][random.randint(0, len(new_offspring_2[j])-1)] = random.uniform(-1, 1)
                    #         new_offspring_1[j+1][random.randint(0, len(new_offspring_1[j+1])-1)] = random.uniform(-1, 1)
                    #         new_offspring_2[j+1][random.randint(0, len(new_offspring_2[j+1])-1)] = random.uniform(-1, 1)

                    new_offspring_1 = deepcopy(parent1)
                    new_offspring_2 = deepcopy(parent2)

                    for l in range(len(parent1)):
                        if parent1[l].ndim > 1:
                            rows, cols = parent1[l].shape
                            row = np.random.randint(0, rows)
                            col = np.random.randint(0, cols)
                        
                            new_offspring_1[l][:row, :] = parent2[l][:row, :] 
                            new_offspring_2[l][:row, :] = parent1[l][:row, :]

                            new_offspring_1[l][row, :col+1] = parent2[l][row, :col+1]
                            new_offspring_2[l][row, :col+1] = parent1[l][row, :col+1]

                            for r in range(rows):
                                for c in range(cols):
                                    new_offspring_1[l][r, c] += (0 if random.uniform(0, 1) > self.mutation_factor/100 else np.random.normal(-1, 1))
                                    new_offspring_2[l][r, c] += (0 if random.uniform(0, 1) > self.mutation_factor/100 else np.random.normal(-1, 1))
                        
                        else:
                            cols = parent1[l].shape[0]
                            col = np.random.randint(0, cols)

                            new_offspring_1[l][:col] = parent2[l][:col]
                            new_offspring_2[l][:col] = parent1[l][:col]

                            for c in range(cols):
                                new_offspring_1[l][c] += (0 if random.uniform(0, 1) > self.mutation_factor/100 else np.random.normal(-1, 1))
                                new_offspring_2[l][c] += (0 if random.uniform(0, 1) > self.mutation_factor/100 else np.random.normal(-1, 1))

                    offspring.append(new_offspring_1)
                    offspring.append(new_offspring_2)

        new_population = []
        new_population.extend(parents_weights_copy)
        new_population.extend(offspring)
        # print('\nPARENT 1')
        # print(parents_weights_copy[0][2][0])
        # print('\nPARENT 2')
        # print(parents_weights_copy[1][2][0])
        # print('\nCHILD 1')
        # print(offspring[0][2][0])
        # print('\nCHILD 2')
        # print(offspring[1][2][0])

        if len(new_population)>len(self.population):
            new_population = new_population[:len(self.population)]

        i=self.n_parents
        while len(new_population)<len(self.population)>i:
            new_population.append(self.population[i].get_weights())
            i+=1

        # for model, weights in zip(self.population, new_population):
        #     model.set_weights(weights)
        for i, weights in enumerate(new_population):
            self.population[i].set_weights(weights)
    

    def run_generation(self):
        self.t.start()

