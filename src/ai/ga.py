import keras
import datetime
import json
import pandas as pd
import numpy as np
import threading
import os
import random
import time
import shutil
import distutils.dir_util
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from ai.model import Model

class GA():

    def __init__(self, engine, control_engine, model, n_in_generation:int, n_generation:int, population_name=False, init_weights=False, n_parents=False, mutation_factor=2, parallel=False, fast_mode=False, prevent_loops=True, populations_path='./!POPULATIONS/', auto_change_map_size=False, print_info=True, previous_path=False):
        self.n_in_gen = n_in_generation
        self.n_gen = n_generation

        self.path = populations_path
        
        self.t = threading.Thread(target=self._run_generation, daemon=True)

        self.n_parents = n_parents if n_parents else self._compute_n_parents()

        self.previous_path = previous_path if previous_path else False

        self.mutation_factor = mutation_factor
        self._prevent_loops = prevent_loops
        self.parallel = parallel
        self.data_check = ''
        self.dir_to_go = ''
        self.time_delay = 0
        self._init_weights = init_weights
        self._name = population_name
        if self._init_weights and len(self._init_weights)!=self.n_in_gen:
            raise Exception('Wrong init weights vector size')
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
        if self.parallel:
            self.model_copies = []
            for _ in range(n_in_generation):
                self.model_copies.append(Model(self.model.n_nodes_input, self.model.n_nodes_output, self.model.n_nodes_hidden, self.model.hidden_activation, self.model.output_activation, biases=True, summary=False))
        else:
            self.model_copies = False


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
        self.folder = self.timestamp.replace(':', '_').replace('.', '_').replace('-', '_') if not self._name else self._name
        while True:
            try:
                os.makedirs(f'{self.path}{self.folder}/models')
                os.makedirs(f'{self.path}{self.folder}/.temp')
                break
            except FileExistsError:
                self.folder = self.folder + '_new'
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

        if self.previous_path:
            distutils.dir_util.copy_tree(f"{self.previous_path}/models", f"{self.path}{self.folder}/models/old_models")
            shutil.copyfile(f"{self.previous_path}/generations_data.csv", f"{self.path}{self.folder}/generations_data.csv")
            shutil.copyfile(f"{self.previous_path}/best_individuals.csv", f"{self.path}{self.folder}/best_individuals.csv")
            shutil.copyfile(f"{self.previous_path}/.temp/.generations_data.temp", f"{self.path}{self.folder}/.temp/.generations_data.temp")
            shutil.copyfile(f"{self.previous_path}/.temp/.best_individuals.temp", f"{self.path}{self.folder}/.temp/.best_individuals.temp")

        for i in range(self.n_in_gen):
            subject = keras.models.clone_model(self.model.model)
            if self._init_weights:
                subject.set_weights(self._init_weights[i])
            population.append(subject)
        
        return population

    
    def _calc_fitness(self, score, n_moves):
        #return (n_moves**2)*(2**score)
        return (score**3)/n_moves


    def _iterate_individuals(self, inp_vector):
        (i, model, local_model, local_control) = inp_vector
        local_s = local_control.s
        self.ind_num += 1
        local_model.model = model
        local_control.load_model(local_model)
        moves = ''
        input_data = []
        starting_pos = (tuple(local_s._head), tuple(local_s._tail[0]))
        apples = []
        apples.append(tuple(local_s._apple))
        last_score = 0
        data_history = []
        
        while not local_s.is_lost:

            while self.pause:
                pass
            
            one_move = time.perf_counter()
            move, data = local_control._move_for_learning()
            if not self.parallel_gen:
                self.data_check = list(data[0])
                self.dir_to_go = move

            if self._prevent_loops:
                #if self.data_check in data_history and local_s.score==last_score:
                #flat_map = str(local_s.map_matrix)
                flat_map = str((local_s._head, local_s._tail, local_s._apple, local_s._direction))
                if flat_map in data_history:
                    local_s.is_lost = True
                    print('LOOPED')
                data_history.append(flat_map)

            moves+=move
            input_data.append(data)

            if local_s.score != last_score:
                data_history = []
                apples.append(local_s._apple)
                last_score+=1

            while time.perf_counter() - one_move < self.time_delay:
                a = 0
                a += 1

        fit = self._calc_fitness(last_score, len(moves))
        self.last_fitness = fit
        if fit > self.highest_fitness_gen:
            self.highest_fitness_gen = fit
            self.highest_fitness_gen_score = last_score
        if fit > self.highest_fitness[0]:
            self.highest_fitness = (fit, self.gen_num)

        info_vector = (i, fit, last_score, (len(moves), moves), starting_pos, apples, input_data, local_model.model.get_weights())

        #if self.print_info:
            #print(f'Gen {self.gen_num}\t|\tIndividual {i+1}/{self.n_in_gen}\t|\tScore: {last_score}\t|\tFitness: {fit}\t|\tTime: {round(time.perf_counter()-start_ind_timer,2)}')

        local_s.is_lost = False    
        
        return info_vector

    
    def _run_generation(self):
        start_gen_timer = time.perf_counter()
        self.parallel_gen = self.parallel
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

        if self.parallel:
            self.control_engine.model = False
            inp = []
            if not self.model_copies:
                self.model_copies = []
                for _ in range(self.n_in_gen):
                    self.model_copies.append(Model(self.model.n_nodes_input, self.model.n_nodes_output, self.model.n_nodes_hidden, self.model.hidden_activation, self.model.output_activation, biases=True, summary=False))

            for i, model in enumerate(self.population):
                inp.append((i, model, self.model_copies[i], deepcopy(self.control_engine)))
            
            with ThreadPoolExecutor(max_workers=self.n_in_gen) as executor:
                results = executor.map(self._iterate_individuals, inp)

        else:
            results = []   
            for i, model in enumerate(self.population):
                results.append(self._iterate_individuals((i, model, self.model, self.control_engine)))

        for info_vector in results:
            gen_dict['Index'].append(info_vector[0])
            gen_dict['Fitness'].append(info_vector[1])
            gen_dict['Score'].append(info_vector[2])
            gen_dict['Moves'].append(info_vector[3])
            gen_dict['Starting position'].append(info_vector[4])
            gen_dict['Apples'].append(info_vector[5])
            gen_dict['Input neurons data'].append(info_vector[6])
            gen_dict['Weights'].append(info_vector[7])

        gen = pd.DataFrame(data=gen_dict.values(), index=gen_dict.keys(), columns=[f'Individual_{n}' for n in gen_dict['Index']])
        row = gen.T.sort_values('Fitness', axis=0, ascending=False).iloc[[0]].set_axis([f'GEN_{self.gen_num}'], axis='index')
        print(row.iloc[:, 0:6])
        row.iloc[:, 0:6].to_csv(f'{self.path}{self.folder}/.temp/.best_individuals.temp', index=True, header=False if self.gen_num>1 or self.previous_path else True, mode='a', sep=';')
        row.iloc[:, 7].to_json(f'{self.path}{self.folder}/models/best_model_gen_{self.gen_num}.json')
        gen.T.iloc[:, 7].to_json(f'{self.path}{self.folder}/models/last_gen_all_models.json')

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

        gen_time = time.perf_counter()-start_gen_timer
        parallel = 'yes' if self.parallel_gen else 'no'
        print(gen.loc['Score'].values)
        print(np.average(gen.loc['Score'].values))
        pd.DataFrame(data=[[gen_time, row.loc[:, 'Score'].values[0], np.average(gen.loc['Score'].values), row.loc[:, 'Fitness'].values[0], parallel]], index=[f'GEN_{self.gen_num}'], columns=['Time[s]', 'Max Score', 'Avg Score', 'Fitness', 'Parallely']).to_csv(f'{self.path}{self.folder}/.temp/.generations_data.temp', index=True, header=False if self.gen_num>1 or self.previous_path else True, mode='a', sep=';')

        if self.print_info:
            print(f'\nGeneration {self.gen_num}: Finished\t|\tTime: {round(gen_time, 2)}s')
            print("PARENTS:")
            print(parents.loc[['Index', 'Fitness', 'Score', 'Moves']])

        try:
            shutil.copy(f'{self.path}{self.folder}/.temp/.generations_data.temp', f'{self.path}{self.folder}/generations_data.csv')
            shutil.copy(f'{self.path}{self.folder}/.temp/.best_individuals.temp', f'{self.path}{self.folder}/best_individuals.csv')
        except:
            print('Close the .csv file')

        if not self.gen_num>=self.n_gen:
            self._run_generation()


    def _crossover(self, parents):
        parents_weights = [parents[individual].loc['Weights'] for individual in parents]
        parents_weights_copy = deepcopy(parents_weights)
        offspring = []

        for i, parent1 in enumerate(parents_weights):
            if i!=len(parents_weights)-1:
                for _, parent2, in enumerate(parents_weights[i+1:]):
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

        if len(new_population)>len(self.population):
            new_population = new_population[:len(self.population)]

        i=self.n_parents
        while len(new_population)<len(self.population)>i:
            new_population.append(self.population[i].get_weights())
            i+=1

        for i, weights in enumerate(new_population):
            self.population[i].set_weights(weights)
    

    def run_generation(self):
        self.t.start()

