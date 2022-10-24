import numpy as np
import pandas as pd
from tkinter import filedialog, Tk
import orjson as json
import os


class SavesHandler:
    def __init__(self, sort_fit=True, cache_gens=False) -> None:
        self.path = None
        self.gen_index = 0
        self.ind_index = 0

        self.cache_gens = cache_gens

        self.sort_fit = sort_fit

        self.import_population()

        
    def get_path(self):
        root = Tk()
        root.withdraw()
        self.path = filedialog.askdirectory()


    def import_population(self):
        self.get_path()

        with open(f'{self.path}/info.json') as f:
            info_dict = json.loads(f.read())['POPULATION INFO']
            self.info_dict = info_dict
            info_pd = pd.DataFrame(info_dict.values(), index=info_dict.keys(), columns=['POPULATION INFO'])
            print(info_pd)

        self.n_of_gens = len(os.listdir(self.path))-1
        self.nn_architecture = info_pd.loc['Neural Network architecture'].values[0][0]
        self.n_in_gen = info_pd.loc['Individuals in generation'].values[0]

        if self.cache_gens:
            self.population = {}
            for i in range(len(os.listdir(self.path))):
                self.population[i] = False


    def import_generation(self, i) -> list:
        try:
            if self.cache_gens:
                if not self.population[i]:
                    with open(f'{self.path}/gen_{i}.json') as f:
                        individuals = json.loads(f.read())
                        gen_frame = pd.DataFrame(individuals, columns=individuals.keys())
                        gen_frame_sorted = gen_frame.sort_values('Fitness', axis=1, inplace=False, ascending=False)

                    self.population[i] = [gen_frame_sorted.iloc[:, 0]['Fitness'], gen_frame_sorted if self.sort_fit else gen_frame]

                return self.population[i]

            else:
                with open(f'{self.path}/gen_{i}.json') as f:
                    individuals = json.loads(f.read())
                    gen_frame = pd.DataFrame(individuals, columns=individuals.keys())
                    gen_frame_sorted = gen_frame.sort_values('Fitness', axis=1, inplace=False, ascending=False)

                return [gen_frame_sorted.iloc[:, 0]['Fitness'], gen_frame_sorted if self.sort_fit else gen_frame]
        
        except FileNotFoundError:
            return self.import_generation_csv(i)

    
    def import_generation_csv(self, i) -> list:
        data = pd.read_csv(f'{self.path}/best_individuals.csv', sep=';')
        return data.iloc[i-2, 1:], data.iloc[i-2, 1:]


    def convert_weights(weights:list) -> np.array:
        output = []
        for i in weights:
            for j in i:
                j = np.array(j)
            i = np.array(i)
            output.append(i)

        return output