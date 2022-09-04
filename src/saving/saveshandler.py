import numpy as np
import pandas as pd
from tkinter import filedialog, Tk
import json
import os


class SavesHandler:
    def __init__(self) -> None:
        self.path = None
        self.gen_index = 0
        self.ind_index = 0

        self.import_population()

        
    def get_path(self):
        root = Tk()
        root.withdraw()
        self.path = filedialog.askdirectory()


    def import_population(self):
        self.get_path()

        with open(f'{self.path}/info.json') as f:
            info_dict = json.load(f)['POPULATION INFO']
            info_pd = pd.DataFrame(info_dict.values(), index=info_dict.keys(), columns=['POPULATION INFO'])
            print(info_pd)

        self.population = {}
        for i in range(len(os.listdir(self.path))):
            self.population[i] = False


    def import_generation(self, i):
        if not self.population[i]:
            with open(f'{self.path}/gen_{i}.json') as f:
                individuals = json.load(f)
                gen_frame = pd.DataFrame(individuals, columns=individuals.keys())
                gen_frame.sort_values('Fitness', axis=1, inplace=True, ascending=False)

            self.population[i] = [gen_frame.iloc[:, 0]['Fitness'], gen_frame]

        return self.population[i]


    def convert_weights(weights:list) -> np.array:
        output = []
        for i in weights:
            for j in i:
                j = np.array(j)
            i = np.array(i)
            output.append(i)

        return output