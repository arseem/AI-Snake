import keras
import datetime
import json
import pandas as pd
import numpy as np
import threading
import os
import random
import time


class GA():

    def __init__(self, engine, control_engine, model, n_in_generation:int, n_generation:int, n_parents=False, mutation_factor=2, fast_mode=False, populations_path='./!POPULATIONS/', auto_change_map_size=False, print_info=True):
        self.n_in_gen = n_in_generation
        self.n_gen = n_generation

        self.path = populations_path
        
        self.t = threading.Thread(target=self._run_generation, daemon=True)

        self.n_parents = n_parents if n_parents else self._compute_n_parents()

        self.mutation_factor = mutation_factor
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
        self.population = self._init_population()


    def _compute_n_parents(self):
        n=0
        while (2+(n-1))*n < self.n_in_gen:
            n+=1
        
        return n


    def _init_population(self):
        self.gen_num = 0
        self.ind_num = 0
        self.last_fitness = 0
        self.highest_fitness = (0, '-')
        self.highest_fitness_gen = 0
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
            'Neural Network architecture': [[self.model.n_nodes_input, (tuple([n for n in self.model.n_nodes_hidden]), self.model.hidden_activation), (self.model.n_nodes_output, self.model.output_activation)]]
        }

        with open(f'{self.path}{self.folder}/info.json', 'w') as f:
            info = pd.DataFrame(data=info_dict.values(), index=info_dict.keys(), columns=['POPULATION INFO'])
            print(info)
            info.to_json(f, orient='columns', indent=4)

        for _ in range(self.n_in_gen):
            subject = keras.models.clone_and_build_model(self.model.model)
            population.append(subject)
        
        return population

    
    def _calc_fitness(self, score, n_moves):
        #return 1000*(score**10)/(n_moves/score) if score!=0 else 1/n_moves
        return n_moves+(2**score+score**2.1*500) - (score**1.2*(0.25*n_moves)**1.3)

    
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
                model = self.model
                self.control_engine.load_model(model)
                moves = ''
                input_data = []
                starting_pos = (tuple(self.s._head), tuple(self.s._tail[0]))
                apples = []
                apples.append(tuple(self.s._apple))
                last_score = 0

                while not self.s.is_lost:
                    one_move = time.perf_counter()
                    move, data = self.control_engine._move_for_learning()
                    moves+=move
                    input_data.append(data)

                    if self.s.score != last_score:
                        apples.append(self.s._apple)
                        last_score+=1

                    while time.perf_counter() - one_move < self.time_delay:
                        a = 0
                        a += 1
                    #print(round(time.perf_counter() - one_move, 4))

                fit = self._calc_fitness(last_score, len(moves))
                self.last_fitness = fit
                if fit > self.highest_fitness_gen:
                    self.highest_fitness_gen = fit
                if fit > self.highest_fitness[0]:
                    self.highest_fitness = (fit, self.gen_num)

                gen_dict['Index'].append(i)
                gen_dict['Fitness'].append(fit)
                gen_dict['Score'].append(last_score)
                gen_dict['Moves'].append((len(moves), moves))
                gen_dict['Starting position'].append(starting_pos)
                gen_dict['Apples'].append(apples)
                gen_dict['Input neurons data'].append(input_data)
                gen_dict['Weights'].append(model.model.get_weights())

                gen = pd.DataFrame(data=gen_dict.values(), index=gen_dict.keys(), columns=[f'Individual_{n}' for n in gen_dict['Index']])
                gen_to_write = gen[[f'Individual_{i}']]

                f.write(f'{add}' + gen_to_write.to_json(orient='columns')[1:-1])
                
                add = ',\n\n'

                if self.print_info:
                    print(f'Gen {self.gen_num}\t|\tIndividual {i+1}/{self.n_in_gen}\t|\tScore: {last_score}\t|\tFitness: {fit}\t|\tTime: {round(time.perf_counter()-start_ind_timer,2)}')

                self.s.is_lost = False
            
            f.write('\n\n}')

        fitness_sum = gen.loc['Fitness'].sum()
        choice_weights = [gen[individual].loc['Fitness']/fitness_sum for individual in gen]
        all_indexes = list(range(self.n_in_gen))
        parents_indexes = []
        for _ in range(self.n_parents):
            new_parent = random.choices(all_indexes, weights=choice_weights)[0]
            parents_indexes.append(new_parent)
            choice_weights.pop(all_indexes.index(new_parent))
            all_indexes.remove(new_parent)

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
            print(f'\nGeneration {self.gen_num}: Finished\t|\tTime: {round(time.perf_counter()-start_gen_timer, 2)}')
            print("PARENTS:")
            print(parents.loc[['Index', 'Fitness', 'Score', 'Moves']])

        if not self.gen_num==self.n_gen:
            self._run_generation()


    def _crossover(self, parents):
        parents_weights = [parents[individual].loc['Weights'] for individual in parents]
        new_parents= []

        for i, parent1 in enumerate(parents_weights):
            if i!=len(parents_weights)-1:
                for j, parent2, in enumerate(parents_weights[i+1:]):
                    new_parent_1 = []
                    new_parent_2 = []

                    for layer1, layer2 in zip(parent1, parent2):
                        pivot = len(layer1)//2
                        # if layer1.ndim==1:
                        #     new_layer1 = np.hstack([layer1[:pivot], layer2[pivot:]])
                        #     new_layer2 = np.hstack([layer2[:pivot], layer1[pivot:]])
                        
                        # else:
                        #     new_layer1 = np.zeros((len(layer1),len(layer1[0])))
                        #     new_layer2 = np.zeros((len(layer1),len(layer1[0])))
                        #     for l in range(len(layer2)):
                        #         sublayer1, sublayer2 = layer1[l], layer2[l]
                                
                        #         new_layer1[l] = np.hstack([sublayer1[:pivot], sublayer2[pivot:]])
                        #         new_layer1[l][random.randint(0, len(new_layer1[l])-1)] = random.uniform(-1, 1)
                        #         new_layer1[l][random.randint(0, len(new_layer1[l])-1)] = random.uniform(-1, 1)

                        #         new_layer2[l] = np.hstack([sublayer2[:pivot], sublayer1[pivot:]])
                        #         new_layer2[l][random.randint(0, len(new_layer1[l])-1)] = random.uniform(-1, 1)
                        #         new_layer2[l][random.randint(0, len(new_layer1[l])-1)] = random.uniform(-1, 1)
                        
                        layer1[pivot:], layer2[pivot:] = layer2[pivot:], layer1[pivot:]
                        new_layer1, new_layer2 = layer1, layer2
                        for l in range(len(new_layer1)):
                            for _ in range(self.mutation_factor):
                                new_layer1[l][random.randint(0, len(new_layer1[l])-1)] = random.uniform(-1, 1)
                                new_layer2[l][random.randint(0, len(new_layer1[l])-1)] = random.uniform(-1, 1)

                        new_parent_1.append(new_layer1)
                        new_parent_2.append(new_layer2)

                    new_parents.append(new_parent_1)
                    new_parents.append(new_parent_2)

        if len(new_parents)>len(self.population):
            new_parents = new_parents[:len(self.population)]

        for model, weights in zip(self.population, new_parents):
            model.set_weights(weights)
    

    def run_generation(self):
        self.t.start()

