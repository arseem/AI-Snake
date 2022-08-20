import threading
import keyboard

class ManualControl:

    def __init__(self, engine, move_interval):
        self.s = engine
        self.move_interval = move_interval
        self.detect_key = threading.Thread(target=self.get_direction, daemon=True)
        self.detect_key.start()
        self.direction = self.s._direction

    def get_direction(self):
        while True:
            if not self.s.is_lost:
                press = keyboard.read_key()

                if press == 'w':
                    self.s.first_move = False
                    self.direction = 'U'
                if press == 's':
                    self.s.first_move = False
                    self.direction = 'D'
                if press == 'a':
                    self.s.first_move = False
                    self.direction = 'L'
                if press == 'd':
                    self.s.first_move = False
                    self.direction = 'R'

            else:
                while True:
                    press = keyboard.read_key()
                    if press == 'space':
                        self.s.is_lost = False
                        self.s.first_move = True
                        break

        
    def move(self):
        t = threading.Timer(self.move_interval, self.move)
        t.daemon = True
        t.start()
        if not self.s.is_lost and not self.s.first_move:
            self.s.make_move(self.direction)