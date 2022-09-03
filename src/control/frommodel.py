from logging import PercentStyle
import threading
from ai import data_prep
import numpy as np

class FromModel:

    def __init__(self, engine, move_interval, vision):
        self.s = engine
        self.move_interval = move_interval
        self.vision_engine = vision
        self.vision_data = False
        self.directions_dict = {0:'U', 1:'D', 2:'L', 3:'R'}

    def load_model(self, model):
        self.model = model
        # model.model.summary()
        
    def move(self):
        if not self.s.is_lost:
            self.vision_data = self.vision_engine.get_distances(self.s.map_matrix)
            data_combined = data_prep.from_vision(self.vision_data, self.s._map_size, mode=self.vision_engine.mode)
            
            if self.model.n_nodes_input > len(data_combined):
                direction_data = [1 if self.s._direction==v else 0 for v in self.directions_dict.values()]
                data_combined.extend(direction_data)

            if self.model.n_nodes_input > len(data_combined):
                tail_direction_data = [1 if self.s.tail_direction==v else 0 for v in self.directions_dict.values()]
                data_combined.extend(tail_direction_data)

            data_for_model = np.array([data_combined])
            prediction = self.model.predict(data_for_model)
            move_predict = np.argmax(prediction, axis=1)
            move = self.directions_dict[int(move_predict)]

            self.s.make_move(move)
            
            #print(len(data_for_model))
            #print(data_for_model)
            #print(move)

        else:
            self.s.is_lost = False

        t = threading.Timer(self.move_interval, self.move)
        t.daemon = True
        t.start()

    def _move_for_learning(self):
        self.vision_data = self.vision_engine.get_distances(self.s.map_matrix)
        data_combined = data_prep.from_vision(self.vision_data, self.s._map_size, mode=self.vision_engine.mode)

        if self.model.n_nodes_input > len(data_combined):
            direction_data = [1 if self.s._direction==v else 0 for v in self.directions_dict.values()]
            data_combined.extend(direction_data)

        if self.model.n_nodes_input > len(data_combined):
            tail_direction_data = [1 if self.s.tail_direction==v else 0 for v in self.directions_dict.values()]
            data_combined.extend(tail_direction_data)

        #data_for_model = np.array(data_combined, ndmin=2)
        data_for_model = np.array([data_combined])
        prediction = self.model.predict(data_for_model)
        move_predict = np.argmax(prediction, axis=1)
        move = self.directions_dict[int(move_predict)]

        # print(data_combined)
        # print(prediction)
        # print(move)

        self.s.make_move(move)
        
        return move, data_for_model