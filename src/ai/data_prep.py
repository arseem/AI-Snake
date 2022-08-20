import numpy as np

def from_vision(vision_data:tuple):
    output = []
    for n in vision_data:
        output.extend(n.values())

    for i in range(len(output)):
        output[i] = 1 if output[i] == True else 0 if output[i] == False else int(output[i])
    
    return output