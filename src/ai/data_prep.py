import numpy as np

def from_vision(vision_data:tuple, map_size, mode):
    output = []
    
    if mode == 'bool':
        walls_normalized = [i/(1.4*map_size) for i in list(vision_data[0].values())]
        #walls_normalized = [1 if i==0 else 0 for i in list(vision_data[0].values())]

        output.extend(walls_normalized)
        apples_and_tail = []
        for n in vision_data[1:]:
            apples_and_tail.extend(n.values())

        for i in range(len(apples_and_tail)):
            apples_and_tail[i] = 1 if apples_and_tail[i] == True else 0 if apples_and_tail[i] == False else int(apples_and_tail[i])

        output.extend(apples_and_tail)

    if mode == 'distance':
        output.extend(vision_data[0].values())
        output.extend(vision_data[1].values())
        output.extend(vision_data[2].values())
        output = [i/(1.4*map_size) for i in output]
        for i in range(len(output)):
            output[i] = -1 if output[i] == False else output[i]

    
    return output