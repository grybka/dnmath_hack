import pygame
from src.gui_core.GUIManager import GUIManager
from src.gui.GUIMainWindow import GUIMainWindow
from src.level_generation.OutdoorLevelGenerator import OutdoorLevelGenerator
from src.level_generation.DungeonLevelGenerator import DungeonLevelGenerator
from src.level.ObjectFactory import load_object_templates
from src.game_engine.GameEngine import GameEngine
from src.level_generation.GameWorldLoader import GameWorldLoader

#Set up the game

load_object_templates("data/objects/weapons.yaml")
load_object_templates("data/objects/object_templates.yaml")
load_object_templates("data/objects/entity_templates.yaml")

world_loader=GameWorldLoader()
world_loader.load_gameworld_file("data/levels/gameworld.yaml")

#level_gen=OutdoorLevelGenerator(20,20,"test")
#level=level_gen.generate()
#level2=DungeonLevelGenerator().generate(20,20,"dungeon_test")



engine=GameEngine(world_loader)
#engine.add_level(level)
#engine.add_level(level2)
#engine.spawn_player()


#Set up the GUI
pygame.init()
pygame.font.init()

displayinfo=pygame.display.Info()
max_x=2*1024
max_y=2*768
if displayinfo.current_w*0.9<max_x:
    max_x=int(displayinfo.current_w*0.9)
if displayinfo.current_h*0.8<max_y:
    max_y=int(displayinfo.current_h*0.8)
resolution=(max_x,max_y)

screen=pygame.display.set_mode(resolution)

clock=pygame.time.Clock()

gui_manager=GUIManager(resolution)
gui_manager.load_style_file("data/style/gui_style.yaml")
print(resolution)
if resolution[0]<1400:
    gui_manager.update_style_with_file("data/style/sizes_lowres.yaml")

main_window=GUIMainWindow(screen.get_width(),screen.get_height(),engine)

gui_manager.add_element(main_window)




running=True
while running:
    clock.tick(60)
    gui_manager.draw_screen(screen)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:
            screen=pygame.display.set_mode( (event.w,event.h) )
            main_window.resize( (0,0,screen.get_width(),screen.get_height() ))
            print("resize event")
        if event.type == pygame.QUIT:
            running=False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running=False
        gui_manager.handle_event(event)
    gui_manager.update(clock.get_time())
pygame.quit()