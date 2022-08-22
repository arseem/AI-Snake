import numpy as np
import pygame as pg
import pygame_gui

class VisualizeBoard:

    def __init__(self, engine, fig_size, control, brain=False, fps=60):
        self.control_engine = control
        self.brain = brain
        self.fps = fps
        self.fig_size = fig_size

        self.s = engine
        self.last_score = -1
        self.size_to_change = False

        self.clock = pg.time.Clock()
        
        self.create_board(self.s.map_matrix)


    def create_board(self, data:np.ndarray):
        pg.init()
        pg.font.init()
        self.font = pg.font.SysFont('Courier New', int(self.fig_size*5.5))
        self.font_small = pg.font.SysFont('Courier New', int(self.fig_size*3.5))
        self.display = pg.display.set_mode((self.fig_size*220, self.fig_size*130))
        self.manager = pygame_gui.UIManager((self.fig_size*220, self.fig_size*130))
        start_val = 10 if self.brain else -np.log(self.control_engine.move_interval)
        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*10, self.fig_size*114, self.fig_size*100, self.fig_size*5), value_range=(0, 10), start_value=start_val, manager=self.manager, object_id='speed')
        self.map_size_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*10, self.fig_size*122, self.fig_size*100, self.fig_size*5), value_range=(4, 50), start_value=40, manager=self.manager, object_id='map_size')
        pg.display.set_caption('Artificially Unintelligent Snake [ A U S ]')
        self._update_surface(data)


    def _change_speed(self, val):
        self.control_engine.move_interval = np.exp(-val)
        if self.brain:
            self.brain.time_delay = 1 - val/10
        
    def _change_map_size(self, val):
        self.size_to_change = val

    
    def _update_surface(self, data):
        surf = pg.surfarray.make_surface(data.T)
        surf = pg.transform.scale(surf, (self.fig_size*100, self.fig_size*100))
        pg.draw.rect(surf, (255, 255, 255), (0, 0, self.fig_size*100, self.fig_size*100), 1)
        speed_label = self.font_small.render('SPEED', 1, (255, 255, 255))
        speed_label_rect = speed_label.get_rect(center=(self.fig_size*60, self.fig_size*116.5))
        map_size_label = self.font_small.render(f'MAP SIZE ({self.map_size_slider.current_value})', 1, (255, 255, 255))
        map_size_rect = map_size_label.get_rect(center=(self.fig_size*60, self.fig_size*124.5))
        

        if self.s.score != self.last_score:
            self.display.fill((26, 13, 0))
            h_score = self.font_small.render(f'HIGH SCORE:  {self.s.high_score}', 1, (255, 255, 255))
            score = self.font_small.render(f'SCORE:       {self.s.score}', 1, (255, 255, 255))
            self.display.blit(h_score, (self.fig_size*120, self.fig_size*10))
            self.display.blit(score, (self.fig_size*120, self.fig_size*15))

        if self.brain:
            break_text = self.font_small.render(f'______________________________', 1, (255, 255, 255))
            n_gen = self.font_small.render(f'GENERATION:  {self.brain.gen_num} / {self.brain.n_gen}', 1, (255, 255, 255))
            n_ind = self.font_small.render(f'INDIVIDUAL:  {self.brain.ind_num} / {self.brain.n_in_gen}', 1, (255, 255, 255))
            movs = self.font_small.render(f'MOVES:       {self.s.moves_without_apple} / {self.s.max_without_apple}', 1, (255, 255, 255))
            h_fit = self.font_small.render(f'HIGHEST FITNESS', 1, (255, 255, 255))
            h_fit_o = self.font_small.render(f'        OVERALL:  {self.brain.highest_fitness[0]} (GEN {self.brain.highest_fitness[1]})', 1, (255, 255, 255))
            h_fit_g = self.font_small.render(f'    CURRENT GEN:  {self.brain.highest_fitness_gen}', 1, (255, 255, 255))
            c_fit = self.font_small.render(f'LAST FITNESS:     {self.brain.last_fitness}', 1, (255, 255, 255))
            
            self.display.blit(break_text, (self.fig_size*120, self.fig_size*17.5))
            self.display.blit(n_gen, (self.fig_size*120, self.fig_size*25))
            self.display.blit(n_ind, (self.fig_size*120, self.fig_size*30))
            self.display.blit(movs, (self.fig_size*120, self.fig_size*35))
            self.display.blit(break_text, (self.fig_size*120, self.fig_size*37.5))
            self.display.blit(h_fit, (self.fig_size*120, self.fig_size*45))
            self.display.blit(h_fit_o, (self.fig_size*120, self.fig_size*50))
            self.display.blit(h_fit_g, (self.fig_size*120, self.fig_size*55))
            self.display.blit(c_fit, (self.fig_size*120, self.fig_size*60))
            
        self.display.blit(surf, (self.fig_size*10, self.fig_size*10))
        self.manager.draw_ui(self.display)
        self.display.blit(speed_label, speed_label_rect)
        self.display.blit(map_size_label, map_size_rect)
        pg.display.update()


    def _lost(self):
        if self.size_to_change:
            self.s._map_size = self.size_to_change
            self.size_to_change = False
            self.s._initialize_game()

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

                    if event.ui_object_id == 'map_size':
                        self._change_map_size(self.map_size_slider.current_value)

                self.manager.process_events(event)

            if not self.s.is_lost:
                self._update_surface(self.s.map_matrix)
            else:
                self.manager.draw_ui(self.display)
                pg.display.update()
                self._lost()

            self.manager.update(self.clock.tick(self.fps)/1000)

        pg.quit()