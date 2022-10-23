import keras
import tensorflow as tf
import numpy as np


class Model:

    def __init__(self, n_nodes_input:int, n_nodes_output:int, n_nodes_hidden:list, hidden_activation:str, output_activation:str, biases=True, summary=True):
        self.n_nodes_input = n_nodes_input
        self.n_nodes_hidden = n_nodes_hidden
        self.n_nodes_output = n_nodes_output
        self.hidden_activation = hidden_activation
        self.output_activation = output_activation

        if biases:
            bias_initializer = tf.keras.initializers.RandomNormal()
        else:
            bias_initializer = 'zeros'
        
        model = keras.Sequential()
        
        model.add(keras.layers.Input(n_nodes_input))

        for n in n_nodes_hidden:
            model.add(keras.layers.Dense(n, activation=hidden_activation, bias_initializer=bias_initializer, kernel_initializer=tf.keras.initializers.GlorotUniform, trainable=False))

        model.add(keras.layers.Dense(n_nodes_output, activation=output_activation, bias_initializer=bias_initializer, kernel_initializer=tf.keras.initializers.GlorotUniform, trainable=False))
        if summary:
            model.summary()
        self.model = model

    def predict(self, data:list):
        return self.model(data)

