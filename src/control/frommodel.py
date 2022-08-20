import threading
from ai import data_prep
import numpy as np

class FromModel:

    def __init__(self, engine, move_interval, vision):
        self.s = engine
        self.move_interval = move_interval
        self.vision_engine = vision
        self.directions_dict = {0:'U', 1:'D', 2:'L', 3:'R'}

    def load_model(self, model):
        self.model = model
        model.model.summary()
        
    def move(self):
        if not self.s.is_lost:
            vision_data = self.vision_engine.get_distances(self.s.map_matrix)
            direction_data = [1 if self.s._direction==v else 0 for v in self.directions_dict.values()]
            
            data_combined = data_prep.from_vision(vision_data)
            data_combined.extend(direction_data)
            data_for_model = np.array(data_combined, ndmin=2)

            move_predict = np.argmax(self.model.predict(data_for_model))
            move = self.directions_dict[move_predict]

            self.s.make_move(move)
            
            #print(len(data_for_model))
            #print(data_for_model)
            #print(move)

        else:
            self.s.is_lost = False

        t = threading.Timer(self.move_interval, self.move)
        #t.daemon = True
        t.start()