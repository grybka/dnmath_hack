import pygame
from collections import deque
from ..gui_core.GUIElement import GUIElement, GUIHAnchor,GUIVAnchor
from ..gui_core.GUIPane import  GUIPane, GUIColLayout, GUIRowLayout
from ..gui_core.GUITextBox import GUILabel, GUITextBox
from .GUIMapView import GUIMapView
from ..actions.EntityAction import *
from ..level.MapCoord import Direction, MapCoord
from .Animations import *
from .GUIActivity import *
from . import GUIEvents
from .GUIStatusPane import GUIStatusPane
from .GUIMainMenu import GUIMainMenu

class GUIMainWindow(GUIElement):
    def __init__(self,width,height,engine):
        super().__init__(rect=(0,0,width,height))
        self.engine=engine

        self.mapview=GUIMapView(engine)
        self.statuspane=GUIStatusPane(engine,self)
        self.mainmenu=GUIMainMenu(engine,(0,0,10,10))

        #ulpane=GUIPane(GUILabel("Map Window"),(0,0,0,0))
        ulpane=GUIPane(self.mapview,(0,0,1,1))

        self.text_window=GUITextBox((0,0,100,100),
                                     my_style={"text_color":(255,255,255),"text_size":20},
                                     anchors=(GUIHAnchor.LEFT,GUIVAnchor.BOTTOM))

        #llpane=GUIPane(GUILabel("Text Window"),(0,0,0,0))
        llpane=GUIPane(self.text_window,(0,0,0,0))

        urpane=GUIPane(self.statuspane,(0,0,0,0))
        lrpane=GUIPane(self.mainmenu,(0,0,0,0))
        #lrpane=GUIPane(GUILabel("Main Menu"),(0,0,0,0))


        left_side=GUIColLayout([ulpane,llpane],(0,0,0,0),element_proportions=[3,1],anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])
        right_side=GUIColLayout([urpane,lrpane],(0,0,0,0),element_proportions=[1,1],anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])
        self.full=GUIRowLayout([left_side,right_side],(0,0,width,height),element_proportions=[3,1],anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])

        self.popup_windows=[]

        self.doing_activity=None
        self.activity_deque=deque()

    def add_popup_window(self,window,anchors=(GUIHAnchor.CENTER,GUIVAnchor.CENTER)):
        if anchors[0]==GUIHAnchor.CENTER:
            window.set_x((self.rect[2]-window.rect[2])//2)
        if anchors[1]==GUIVAnchor.CENTER:
            window.set_y((self.rect[3]-window.rect[3])//2)
        self.popup_windows.append(window)

    def remove_popup_window(self,window):
        self.popup_windows.remove(window)

    def add_activity(self,activity):
        if self.doing_activity is None:
            self.doing_activity=activity
        else:
            self.activity_deque.append(activity)

    def handle_event(self,event,window_offset=(0,0)):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.move_in_direction(Direction.N)
            elif event.key == pygame.K_DOWN:
                self.move_in_direction(Direction.S)
            elif event.key == pygame.K_LEFT:
                self.move_in_direction(Direction.W)
            elif event.key == pygame.K_RIGHT:
                self.move_in_direction(Direction.E)
#        if event.type == GUIEvents.CELL_SELECTED_EVENT:
#            print("cell selected {}".format(event.cell))
        for window in self.popup_windows:
            if window.handle_event(event,window_offset=window_offset):
                return True
        return self.full.handle_event(event,window_offset=window_offset)

    def update(self,clock_time):
        #window offset is what I should subtract from mouse events to get the mouse position relative to this element
        if self.doing_activity is not None:
            if self.doing_activity.update(clock_time):
                self.doing_activity=None
                if len(self.activity_deque)>0:
                    self.doing_activity=self.activity_deque.popleft()
            #print("doing activity")
            ... #TODO do activity
        else:
            if not self.engine.messages_pending():
                self.engine.update_timestep()
            if self.engine.messages_pending():
                self.handle_engine_message(self.engine.pop_message())

        for window in self.popup_windows:
            window.update(clock_time)
        return self.full.update(clock_time)

    #draws this element onto the given surface
    def draw_screen(self,surf):
        full_redrawn=self.full.draw_screen(surf)
        for window in self.popup_windows:
            if full_redrawn:
                window.a_redraw_is_needed()
            window.draw_screen(surf)

    def resize(self,rect):
        super().resize(rect)
        self.full.resize((0,0,rect[2],rect[3]))

    def move_in_direction(self,direction):
        new_pos=self.engine.get_player().get_pos()+MapCoord.direction_to_vector(direction)
        #if there is a monster in the way, attack it
        objects=self.engine.level.map.get_objects_in_cell(new_pos)
        for object in objects:
            if isinstance(object,Entity):
                self.engine.set_player_action(MeleeAction(self.engine.get_player(),self.engine,object))
                return

        self.engine.set_player_action(MoveAction(self.engine.get_player(),self.engine,direction))
        ...

    def handle_engine_message(self,message):
        self.mapview.handle_engine_message(message)
        self.statuspane.handle_engine_message(message)
        if message.message_type=="ObjectMoved":
            activity=GUIWaitForMapAnimation(self,self.engine,self.mapview.add_move_animation(message.objid,message.oldpos,message.pos,100))
            self.add_activity(activity)
        if message.message_type=="InfoText":
            self.text_window.print(message.text)
        if message.message_type=="ActionFailed":
            self.text_window.print(message.reason)
        if message.message_type=="MeleeAttack":
            self.text_window.print(message.message)
        if message.message_type=="RangedAttack":
            self.text_window.print(message.message)
            anim=MapAnimationMissile(self.mapview,self.engine,"arrow",message.start_pos,message.end_pos,500)
            activity=GUIWaitForMapAnimation(self,self.engine,self.mapview.add_animation(anim))
            self.add_activity(activity)
        if message.message_type=="CreatureDeath":
            ret=MapAnimationShakingSprite(self.mapview,self.engine,message.cell_pos,"skullnbones",500)
            self.add_activity(GUIWaitForMapAnimation(self,self.engine,self.mapview.add_animation(ret)))
            self.text_window.print("{} is defeated.".format(message.creature.reference_noun(specific=True)))
