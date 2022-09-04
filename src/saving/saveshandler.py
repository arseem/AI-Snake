from this import d
import numpy as np
import pandas as pd
import threading
from tkinter import filedialog, Tk
import orjson as json
import os


class SavesHandler:
    def __init__(self, sort_fit=True) -> None:
        self.path = None
        self.gen_index = 0
        self.ind_index = 0

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
            info_pd = pd.DataFrame(info_dict.values(), index=info_dict.keys(), columns=['POPULATION INFO'])
            print(info_pd)

        self.population = {}
        for i in range(len(os.listdir(self.path))):
            self.population[i] = False


    def import_generation(self, i) -> list:
        if not self.population[i]:
            with open(f'{self.path}/gen_{i}.json') as f:
                individuals = json.loads(f.read())
                gen_frame = pd.DataFrame(individuals, columns=individuals.keys())
                gen_frame_sorted = gen_frame.sort_values('Fitness', axis=1, inplace=False, ascending=False)

            self.population[i] = [gen_frame_sorted.iloc[:, 0]['Fitness'], gen_frame_sorted if self.sort_fit else gen_frame]

        return self.population[i]


    def convert_weights(weights:list) -> np.array:
        output = []
        for i in weights:
            for j in i:
                j = np.array(j)
            i = np.array(i)
            output.append(i)

        return output