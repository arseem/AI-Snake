import threading

class FromSave:

    def __init__(self, engine, move_interval):
        self.s = engine
        self.move_interval = move_interval

    def load_string(self, save):
        self.moves = list(save)
        
    def move(self):
        t = threading.Timer(self.move_interval, self.move)
        t.daemon = True
        t.start()
        if not self.s.is_lost and self.moves:
            self.s.make_move(self.moves.pop(0))
        
        else:
            t.cancel()
