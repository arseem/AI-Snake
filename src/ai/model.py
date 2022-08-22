import keras
import numpy as np


class Model:

    def __init__(self, n_nodes_input:int, n_nodes_output:int, n_nodes_hidden:list, hidden_activation:str, output_activation:str):
        self.n_nodes_input = n_nodes_input
        self.n_nodes_hidden = n_nodes_hidden
        self.n_nodes_output = n_nodes_output
        self.hidden_activation = hidden_activation
        self.output_activation = output_activation
        
        model = keras.Sequential()
        
        model.add(keras.layers.Dense(n_nodes_input, input_shape=(n_nodes_input,)))

        for n in n_nodes_hidden:
            model.add(keras.layers.Dense(n, activation=hidden_activation))

        model.add(keras.layers.Dense(n_nodes_output, activation=output_activation))

        self.model = model
        self.model.compile(optimizer = keras.optimizers.Adam())

    def predict(self, data:list):
        return self.model.predict(data, verbose=0)

