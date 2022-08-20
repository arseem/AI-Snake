import numpy as np
import pygame as pg
import pygame_gui

class VisualizeBoard:

    def __init__(self, engine, fig_size, control, fps=60):
        self.control_engine = control
        self.fps = fps
        self.fig_size = fig_size

        self.s = engine
        self.last_score = -1

        self.clock = pg.time.Clock()
        
        self.create_board(self.s.map_matrix)


    def create_board(self, data:np.ndarray):
        pg.init()
        pg.font.init()
        self.font = pg.font.SysFont('Courier New', int(self.fig_size*5.5))
        self.font_small = pg.font.SysFont('Courier New', int(self.fig_size*3.5))
        self.display = pg.display.set_mode((self.fig_size*120, self.fig_size*120))
        self.manager = pygame_gui.UIManager((self.fig_size*120, self.fig_size*120))
        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*10, self.fig_size*112, self.fig_size*100, self.fig_size*5), value_range=(0, 10), start_value=-np.log(self.control_engine.move_interval), manager=self.manager, object_id='speed')
        pg.display.set_caption('Artificially Unintelligent Snake [ A U S ]')
        self._update_surface(data)


    def _change_speed(self, val):
        self.control_engine.move_interval = np.exp(-val)

    
    def _update_surface(self, data):
        surf = pg.surfarray.make_surface(data.T)
        surf = pg.transform.scale(surf, (self.fig_size*100, self.fig_size*100))
        pg.draw.rect(surf, (255, 255, 255), (0, 0, self.fig_size*100, self.fig_size*100), 1)
        speed_label = self.font_small.render('SPEED', 1, (255, 255, 255))
        speed_label_rect = speed_label.get_rect(center=(self.fig_size*60, self.fig_size*114.5))
        

        if self.s.score != self.last_score:
            self.display.fill((26, 13, 0))
            h_score = self.font_small.render(f'HIGH SCORE:  {self.s.high_score}', 1, (255, 255, 255))
            score = self.font_small.render(f'SCORE:       {self.s.score}', 1, (255, 255, 255))
            self.display.blit(h_score, (self.fig_size*10, self.fig_size*1.5))
            self.display.blit(score, (self.fig_size*10, self.fig_size*5.5))
        
        self.display.blit(surf, (self.fig_size*10, self.fig_size*10))
        self.manager.draw_ui(self.display)
        self.display.blit(speed_label, speed_label_rect)
        pg.display.update()


    def _lost(self):
        lost1 = self.font.render('YOU LOST', 1, (255, 255, 255))
        lost1_rect = lost1.get_rect(center=(self.fig_size*60, self.fig_size*55))
        lost2 = self.font.render('PRESS SPACEBAR TO RESTART', 1, (255, 255, 255))
        lost2_rect = lost2.get_rect(center=(self.fig_size*60, self.fig_size*65))
        self.display.blit(lost1, lost1_rect)
        self.display.blit(lost2, lost2_rect)
        pg.display.update()


    def run_board(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.USEREVENT:
                    if event.ui_object_id == 'speed':
                        self._change_speed(self.speed_slider.current_value)

                self.manager.process_events(event)

            if not self.s.is_lost:
                self._update_surface(self.s.map_matrix)
            else:
                self.manager.draw_ui(self.display)
                pg.display.update()
                self._lost()

            self.manager.update(self.clock.tick(self.fps)/1000)

        pg.quit()