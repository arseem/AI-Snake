import numpy as np
import pygame as pg
import pygame_gui
from pygame import gfxdraw
def circle_draw(surface, color, xy, radius):
    gfxdraw.aacircle(surface, int(xy[0]), int(xy[1]), radius, color)
    gfxdraw.filled_circle(surface, int(xy[0]), int(xy[1]), radius, color)

pg.draw.circle = circle_draw

class VisualizeBoard:

    def __init__(self, engine, fig_size, control, brain=False, fps=60):
        self.control_engine = control
        self.brain = brain
        if brain:
            self.brain_mode = 'save' if hasattr(brain, 'save') else 'ai'
        self.fps = fps
        self.fig_size = fig_size

        self.s = engine
        self.last_score = -1
        self.size_to_change = False
        self.draw_vision_lines = False

        self.clock = pg.time.Clock()
        
        self.create_board(self.s.map_matrix)


    def create_board(self, data:np.ndarray):
        pg.init()
        pg.font.init()
        self.font = pg.font.SysFont('Courier New', int(self.fig_size*5.5))
        self.font_small = pg.font.SysFont('Courier New', int(self.fig_size*3.5))
        self.font_smallest = pg.font.SysFont('Courier New', int(self.fig_size*2))
        if self.brain:
            self.display = pg.display.set_mode((self.fig_size*270, self.fig_size*130), pg.RESIZABLE)
            self.manager = pygame_gui.UIManager((self.fig_size*270, self.fig_size*130))
        else:
            self.display = pg.display.set_mode((self.fig_size*180, self.fig_size*130), pg.RESIZABLE)
            self.manager = pygame_gui.UIManager((self.fig_size*180, self.fig_size*130))
        self.map_size_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*10, self.fig_size*122, self.fig_size*100, self.fig_size*5), value_range=(4, 50), start_value=self.s._map_size, manager=self.manager, object_id='map_size')
        if self.brain:
            if self.brain_mode=='ai':
                self.mutation_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*120, self.fig_size*105, self.fig_size*90, self.fig_size*5), value_range=(0, self.brain.n_parents*10), start_value=2, manager=self.manager, object_id='mutation')
                self.parents_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*120, self.fig_size*97, self.fig_size*90, self.fig_size*5), value_range=(2, self.brain.n_in_gen), start_value=self.brain.n_parents, manager=self.manager, object_id='parents')
                self.speed_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*10, self.fig_size*114, self.fig_size*100, self.fig_size*5), value_range=(0, 100), start_value=100, manager=self.manager, object_id='speed')
                self.lines_button = pygame_gui.elements.UIButton(pg.rect.Rect(self.fig_size*180, self.fig_size*115, self.fig_size*25, self.fig_size*10), text='VISION LINES', manager=self.manager, object_id='lines_button')
                self.parallel_button = pygame_gui.elements.UIButton(pg.rect.Rect(self.fig_size*120, self.fig_size*82, self.fig_size*25, self.fig_size*10), text='PARALLEL', manager=self.manager, object_id='parallel_button')

            else:
                self.speed_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*10, self.fig_size*114, self.fig_size*100, self.fig_size*5), value_range=(0, 10), start_value=-np.log(self.control_engine.move_interval), manager=self.manager, object_id='speed')
                self.ind_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*120, self.fig_size*105, self.fig_size*90, self.fig_size*5), value_range=(1, self.brain.n_in_gen), start_value=1, manager=self.manager, object_id='ind')
                self.gen_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*120, self.fig_size*97, self.fig_size*90, self.fig_size*5), value_range=(1, self.brain.n_gen-1), start_value=1, manager=self.manager, object_id='gen')
                self.load_button = pygame_gui.elements.UIButton(pg.rect.Rect(self.fig_size*180, self.fig_size*115, self.fig_size*25, self.fig_size*10), text='LOAD SNAKE', manager=self.manager, object_id='load_button')

        else:
            self.speed_slider = pygame_gui.elements.UIHorizontalSlider(pg.rect.Rect(self.fig_size*10, self.fig_size*114, self.fig_size*100, self.fig_size*5), value_range=(0, 10), start_value=-np.log(self.control_engine.move_interval), manager=self.manager, object_id='speed')
        self.menu_button = pygame_gui.elements.UIButton(pg.rect.Rect(self.fig_size*150, self.fig_size*115, self.fig_size*25, self.fig_size*10), text='MENU', manager=self.manager, object_id='menu_button')
        self.pause_button = pygame_gui.elements.UIButton(pg.rect.Rect(self.fig_size*120, self.fig_size*115, self.fig_size*25, self.fig_size*10), text='PAUSE', manager=self.manager, object_id='pause_button')

        pg.display.set_caption('Artificially Unintelligent Snake [ A U S ]')
        self._update_surface(data)


    def _change_speed(self, val):
        self.control_engine.move_interval = np.exp(-val)
        if self.brain:
            if self.brain_mode == 'ai':
                self.brain.time_delay = (100-val)/100
        
    def _change_map_size(self, val):
        self.size_to_change = val

    def _change_mutation(self, val):
        self.brain.mutation_factor = val

    def _change_n_parents(self, val):
        self.brain.n_parents = val
    
    def _change_individual(self, val):
        self.brain.ind_num_set = val

    def _change_generation(self, val):
        self.brain.gen_num_set = val

    def _change_pause(self):
        if self.brain:
            self.brain.pause = not self.brain.pause
            self.pause_button.set_text('PLAY' if self.brain.pause else 'PAUSE')
        
        else:
            self.control_engine.pause = not self.control_engine.pause
            self.pause_button.set_text('PLAY' if self.control_engine.pause else 'PAUSE')

    
    def _update_surface(self, data):
        surf = pg.surfarray.make_surface(data.T)
        surf = pg.transform.scale(surf, (self.fig_size*100, self.fig_size*100))
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
            if self.brain_mode == 'ai':
                x_h, y_h = (self.fig_size*100/self.s._map_size * self.s._head[0] + self.fig_size*100/self.s._map_size/2, self.fig_size*100/self.s._map_size * self.s._head[1] + self.fig_size*100/self.s._map_size/2)
                vision_data = self.control_engine.vision_data
                if vision_data and self.draw_vision_lines:
                    head_xy = (x_h, y_h)
                    w = (0, y_h)
                    e = (self.fig_size*100, y_h)
                    n = (x_h, 0)
                    s = (x_h, self.fig_size*100)
                    nw = (x_h-self.fig_size*100, y_h-self.fig_size*100)
                    ne = (x_h+self.fig_size*100, y_h-self.fig_size*100)
                    sw = (x_h-self.fig_size*100, y_h+self.fig_size*100)
                    se = (x_h+self.fig_size*100, y_h+self.fig_size*100)
                    
                    pg.draw.line(surf, 100 if vision_data[1]['w'] else (0, 255, 38) if vision_data[2]['w'] else (231, 235, 204), head_xy, w, width=1) 
                    pg.draw.line(surf, 100 if vision_data[1]['e'] else (0, 255, 38) if vision_data[2]['e'] else (231, 235, 204), head_xy, e, width=1)
                    pg.draw.line(surf, 100 if vision_data[1]['n'] else (0, 255, 38) if vision_data[2]['n'] else (231, 235, 204), head_xy, n, width=1) 
                    pg.draw.line(surf, 100 if vision_data[1]['s'] else (0, 255, 38) if vision_data[2]['s'] else (231, 235, 204), head_xy, s, width=1)
                    pg.draw.line(surf, 100 if vision_data[1]['nw'] else (0, 255, 38) if  vision_data[2]['nw'] else (231, 235, 204), head_xy, nw, width=1)  
                    pg.draw.line(surf, 100 if vision_data[1]['ne'] else (0, 255, 38) if  vision_data[2]['ne'] else (231, 235, 204), head_xy, ne, width=1)  
                    pg.draw.line(surf, 100 if vision_data[1]['sw'] else (0, 255, 38) if  vision_data[2]['sw'] else (231, 235, 204), head_xy, sw, width=1)  
                    pg.draw.line(surf, 100 if vision_data[1]['se'] else (0, 255, 38) if  vision_data[2]['se'] else (231, 235, 204), head_xy, se, width=1)  
                
            break_text = self.font_small.render(f'______________________________', 1, (255, 255, 255))
            n_gen = self.font_small.render(f'GENERATION:  {self.brain.gen_num} / {self.brain.n_gen}', 1, (255, 255, 255))
            n_ind = self.font_small.render(f'INDIVIDUAL:  {self.brain.ind_num} / {self.brain.n_in_gen}', 1, (255, 255, 255))
            movs = self.font_small.render(f'MOVES:       {self.s.moves_without_apple} / {self.s.max_without_apple}', 1, (255, 255, 255))
            h_fit = self.font_small.render(f'HIGHEST FITNESS', 1, (255, 255, 255))
            h_fit_o = self.font_small.render(f'        OVERALL:  {self.brain.highest_fitness[0]} (GEN {self.brain.highest_fitness[1]})', 1, (255, 255, 255))
            h_fit_g = self.font_small.render(f'    CURRENT GEN:  {self.brain.highest_fitness_gen}', 1, (255, 255, 255))
            c_fit = self.font_small.render(f'LAST FITNESS:     {self.brain.last_fitness}' if self.brain_mode=='ai' else f'CURRENT FITNESS:  {self.brain.last_fitness}', 1, (255, 255, 255))

            len_inp = len(self.brain.data_check)
            inp_centers = []
            for i, v in enumerate(self.brain.data_check):
                pg.draw.circle(self.display, (int(255*v), 0, 0) if v>=0 else (0, 0, 0), (self.fig_size*228, int(1.8*self.fig_size*120/len_inp)+int(i*self.fig_size*120/len_inp)), int(self.fig_size))
                inp_centers.append((self.fig_size*228, int(1.8*self.fig_size*120/len_inp)+int(i*self.fig_size*120/len_inp)))
                self.display.blit(self.font_smallest.render(str(round(v, 2) if v not in (0, 1, -1) else '   1' if v==1 else '  -1' if v==-1 else '   0'), 1, (255, 255, 255)), (self.fig_size*220, int(1.8*0.9*self.fig_size*120/len_inp)+int(i*self.fig_size*120/len_inp)))
            
            h_layers = self.brain.n_nodes_hidden
            n_h_layers = len(h_layers)
            h_centers = []
            for n, j in enumerate(h_layers):
                h_centers.append([])
                for i in range(j):
                    pg.draw.circle(self.display, (0, 0, 0), (self.fig_size*228+self.fig_size*15/(n_h_layers)*(n+1), int(1.2*self.fig_size*120/j)+int(i*self.fig_size*120/j)), int(self.fig_size))
                    h_centers[n].append((self.fig_size*228+self.fig_size*15/(n_h_layers)*(n+1), int(1.2*self.fig_size*120/j)+int(i*self.fig_size*120/j)))

            n_out = self.brain.n_nodes_output
            out_centers = []
            direction = self.brain.dir_to_go
            directions = ['U', 'D', 'L', 'R']
            for i in range(n_out):
                pg.draw.circle(self.display, (255 if direction==directions[i] else 0, 0, 0), (self.fig_size*228+self.fig_size*30, int(1.8*self.fig_size*120/n_out)+int(i*self.fig_size*120/n_out/4)), int(self.fig_size))
                out_centers.append((self.fig_size*228+self.fig_size*30, int(1.8*self.fig_size*120/n_out)+int(i*self.fig_size*120/n_out/4)))
                self.display.blit(self.font_smallest.render(directions[i], 1, (255, 255, 255)), (self.fig_size*228+self.fig_size*32, int(1.8*self.fig_size*120/n_out)+int(i*self.fig_size*120/n_out/4)))

            centers = [inp_centers, *h_centers, out_centers]
            for i in range(1, len(centers)):
                for x in centers[i]:
                    for y in centers[i-1]:
                        pg.draw.aaline(self.display, (0, 0, 0), (x[0]-int(self.fig_size), x[1]), (y[0]+int(self.fig_size), y[1]))  

            self.display.blit(break_text, (self.fig_size*120, self.fig_size*17.5))
            self.display.blit(n_gen, (self.fig_size*120, self.fig_size*25))
            self.display.blit(n_ind, (self.fig_size*120, self.fig_size*30))
            self.display.blit(movs, (self.fig_size*120, self.fig_size*35))
            self.display.blit(break_text, (self.fig_size*120, self.fig_size*37.5))
            self.display.blit(h_fit, (self.fig_size*120, self.fig_size*45))
            self.display.blit(h_fit_o, (self.fig_size*120, self.fig_size*50))
            self.display.blit(h_fit_g, (self.fig_size*120, self.fig_size*55))
            self.display.blit(c_fit, (self.fig_size*120, self.fig_size*60))
            
            
        pg.draw.rect(surf, (255, 255, 255), (0, 0, self.fig_size*100, self.fig_size*100), 1)
        self.display.blit(surf, (self.fig_size*10, self.fig_size*10))
        self.manager.draw_ui(self.display)
        self.display.blit(speed_label, speed_label_rect)
        self.display.blit(map_size_label, map_size_rect)
        if self.brain:
            if self.brain_mode=='ai':
                mut_label = self.font_small.render(f'MUTATION FACTOR ({self.brain.mutation_factor})', 1, (255, 255, 255))
                mut_rect = map_size_label.get_rect(center=(self.fig_size*160, self.fig_size*107.5))
                parents_label = self.font_small.render(f'NUMBER OF PARENTS ({self.brain.n_parents})', 1, (255, 255, 255))
                parents_rect = map_size_label.get_rect(center=(self.fig_size*157.5, self.fig_size*99.5))
                self.display.blit(mut_label, mut_rect)
                self.display.blit(parents_label, parents_rect)
            
            else:
                ind_label = self.font_small.render(f'INDIVIDUAL ({self.brain.ind_num_set})', 1, (255, 255, 255))
                ind_rect = map_size_label.get_rect(center=(self.fig_size*160, self.fig_size*107.5))
                gen_label = self.font_small.render(f'GENERATION ({self.brain.gen_num_set})', 1, (255, 255, 255))
                gen_rect = map_size_label.get_rect(center=(self.fig_size*160, self.fig_size*99.5))
                self.display.blit(ind_label, ind_rect)
                self.display.blit(gen_label, gen_rect)
        pg.display.update()


    def _lost(self):
        if self.size_to_change:
            self.s._map_size = self.size_to_change
            self.size_to_change = False
            self.s._initialize_game()

        if not self.brain:
            lost1 = self.font.render('YOU LOST', 1, (255, 255, 255))
            lost1_rect = lost1.get_rect(center=(self.fig_size*60, self.fig_size*55))
            lost2 = self.font.render('PRESS SPACEBAR TO RESTART', 1, (255, 255, 255))
            lost2_rect = lost2.get_rect(center=(self.fig_size*60, self.fig_size*65))
            self.display.blit(lost1, lost1_rect)
            self.display.blit(lost2, lost2_rect)
        else:
            lost1 = self.font.render(f'{self.brain.ind_num} / {self.brain.n_in_gen}', 1, (255, 255, 255))
            lost1_rect = lost1.get_rect(center=(self.fig_size*60, self.fig_size*55))
            self.display.blit(lost1, lost1_rect)
        
        if self.brain:
            if self.brain_mode=='save':
                self.ind_slider.set_current_value(self.brain.ind_num)
                self.gen_slider.set_current_value(self.brain.gen_num)
        pg.display.update()


    def run_board(self):
        running = True
        output = 0
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_object_id == 'speed':
                        self._change_speed(self.speed_slider.current_value)

                    if event.ui_object_id == 'map_size':
                        self._change_map_size(self.map_size_slider.current_value)

                    if event.ui_object_id == 'mutation':
                        self._change_mutation(self.mutation_slider.current_value)

                    if event.ui_object_id == 'parents':
                        self._change_n_parents(self.parents_slider.current_value)

                    if event.ui_object_id == 'ind':
                        self._change_individual(self.ind_slider.current_value)

                    if event.ui_object_id == 'gen':
                        self._change_generation(self.gen_slider.current_value)

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_object_id == 'menu_button':
                        output = 1
                        if self.brain:
                            self.brain.n_gen = self.brain.gen_num
                            self.brain.t.join()
                        running = False

                    if event.ui_object_id == 'pause_button':
                        self._change_pause()

                    if event.ui_object_id == 'lines_button':
                        self.draw_vision_lines = not self.draw_vision_lines

                    if event.ui_object_id == 'parallel_button':
                        self.brain.parallel = not self.brain.parallel

                    if event.ui_object_id == 'load_button':
                        self.brain.load_individual()

                self.manager.process_events(event)

            if not self.s.is_lost:
                self._update_surface(self.s.map_matrix)
            else:
                self.manager.draw_ui(self.display)
                pg.display.update()
                self._lost()

            self.manager.update(self.clock.tick(self.fps)/1000)

        pg.quit()
        return output