import pygame as pg
import pygame_gui

class Menu:

    def __init__(self, fig_size, set, fps=60):
        self.settings = set
        self.fps = fps
        self.fig_size = fig_size

        self.clock = pg.time.Clock()
        
        self.create_menu()


    def create_menu(self):
        pg.init()
        pg.font.init()
        self.font = pg.font.SysFont('Courier New', int(self.fig_size*5.5))
        self.font_small = pg.font.SysFont('Courier New', int(self.fig_size*3.5))
        self.font_smallest = pg.font.SysFont('Courier New', int(self.fig_size*2))
        self.display = pg.display.set_mode((self.fig_size*70, self.fig_size*80), pg.RESIZABLE)
        self.manager = pygame_gui.UIManager((self.fig_size*70, self.fig_size*80))
        
        self.inputs = []

        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*5, self.fig_size*27, self.fig_size*5), manager=self.manager))
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*10, self.fig_size*27, self.fig_size*5), manager=self.manager))
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*15, self.fig_size*27, self.fig_size*5), manager=self.manager))
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*20, self.fig_size*27, self.fig_size*5), manager=self.manager))
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*25, self.fig_size*27, self.fig_size*5), manager=self.manager))   
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*30, self.fig_size*27, self.fig_size*5), manager=self.manager))
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*35, self.fig_size*27, self.fig_size*5), manager=self.manager))       
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*40, self.fig_size*27, self.fig_size*5), manager=self.manager))      
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*45, self.fig_size*27, self.fig_size*5), manager=self.manager))     
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*50, self.fig_size*27, self.fig_size*5), manager=self.manager))    
        self.inputs.append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.rect.Rect(self.fig_size*35, self.fig_size*55, self.fig_size*27, self.fig_size*5), manager=self.manager))

        for inp, sett in zip(self.inputs, self.settings):
            inp.set_text(str(sett))

        for i, text in enumerate(('MAP SIZE:', 'IND IN GEN:', 'N OF GEN:', 'N OF PARENTS:', 'VISION MODE:', 'INPUT NODES:', 'OUTPUT NODES:', 'HIDDEN NODES:', 'HIDDEN ACT:', 'OUTPUT ACT:', 'SAVES PATH:')):
            label = self.font_small.render(text, 1, (255, 255, 255))    
            self.display.blit(label, (self.fig_size*3, self.fig_size*5+self.fig_size*5*i))

        self.ai_button = pygame_gui.elements.UIButton(pg.rect.Rect(self.fig_size*3, self.fig_size*65, self.fig_size*20, self.fig_size*5), text='NEW', manager=self.manager, object_id='ai_button')
        self.resume_button = pygame_gui.elements.UIButton(pg.rect.Rect(self.fig_size*3, self.fig_size*70, self.fig_size*20, self.fig_size*5), text='RESUME', manager=self.manager, object_id='resume_button')
        self.saved_button = pygame_gui.elements.UIButton(pg.rect.Rect(self.fig_size*25, self.fig_size*65, self.fig_size*20, self.fig_size*10), text='LOAD', manager=self.manager, object_id='saved_button')
        self.play_button = pygame_gui.elements.UIButton(pg.rect.Rect(self.fig_size*47, self.fig_size*65, self.fig_size*20, self.fig_size*10), text='PLAY', manager=self.manager, object_id='play_button')
  
        self.manager.update(self.fps/1000)
        pg.display.set_caption('MENU')


    def run_menu(self):
        running = True
        output = 0
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    output = 0
                    running = False

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_object_id == 'ai_button':
                        output = 1

                    if event.ui_object_id == 'saved_button':
                        output = 2

                    if event.ui_object_id == 'play_button':
                        output = 3

                    if event.ui_object_id == 'resume_button':
                        output = 4

                    running = False

                self.manager.process_events(event)
                self.manager.draw_ui(self.display)
                pg.display.update()

            self.manager.update(self.clock.tick(self.fps)/1000)

        pg.quit()
        return output, [i.get_text() for i in self.inputs]