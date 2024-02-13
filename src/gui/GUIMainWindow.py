import pygame
from collections import deque
from ..gui_core.GUIElement import GUIElement, GUIHAnchor,GUIVAnchor
from ..gui_core.GUIPane import  GUIPane, GUIColLayout, GUIRowLayout
from ..gui_core.GUITextBox import GUILabel, GUITextBox
from .GUIMapView import GUIMapView
from ..actions.EntityAction import *
from ..level.MapCoord import Direction, MapCoord
from ..level.GraphPaperMap import WallType
from .Animations import *
from .GUIActivity import *
from . import GUIEvents
from .GUIStatusPane import GUIStatusPane
from .GUIMainMenu import GUIMainMenu
from .GUICellPopup import GUICellPopup
from .GUIInfoPopup import GUIInfoPopup

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

    def add_popup_window(self,window,anchors=(GUIHAnchor.CENTER,GUIVAnchor.CENTER),location=None):
        if location is not None:
            window.set_x(location[0])
            window.set_y(location[1])
        else:
            if anchors[0]==GUIHAnchor.CENTER:
                window.set_x((self.rect[2]-window.rect[2])//2)
            if anchors[1]==GUIVAnchor.CENTER:
                window.set_y((self.rect[3]-window.rect[3])//2)
        #TODO fix any issues where the window is off screen
        if window.rect[0]+window.rect[2]>self.rect[2]:
            window.set_x(self.rect[2]-window.rect[2])
        if window.rect[1]+window.rect[3]>self.rect[3]:
            window.set_y(self.rect[3]-window.rect[3])
        if window.rect[0]<0:
            window.set_x(0)
        if window.rect[1]<0:
            window.set_y(0)
        self.popup_windows.append(window)

    def remove_popup_window(self,window):
        self.popup_windows.remove(window)

    def add_activity(self,activity):
        if self.doing_activity is None:
            self.doing_activity=activity
            self.doing_activity.start()
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
            elif event.key == pygame.K_PERIOD:
                self.engine.set_player_action(WaitAction(self.engine.get_player(),self.engine))
        if event.type == GUIEvents.CELL_SELECTED_EVENT:
            if event.cell is not None:                
                print("cell selected event")
                #figure out a nice place to put the window
                cell_popup=GUICellPopup(self.engine,self,event.cell)
                pixel=self.mapview.cell_to_pixel(event.cell)
                if pixel[0]>self.rect[2]//2:
                    pixel=(int(pixel[0]-cell_popup.rect[2]-0.5*self.mapview.pixels_per_grid),int(pixel[1]))
                else:
                    pixel=(int(pixel[0]+2*self.mapview.pixels_per_grid),int(pixel[1]))
                #remove any existing cell popup
                for window in self.popup_windows:
                    self.remove_popup_window(window)
                self.add_popup_window(cell_popup,location=pixel)
        if event.type == GUIEvents.CELL_RIGHTCLICKED_EVENT:
            if event.cell is not None:
                self.handle_cell_rightclick(event)

        for window in self.popup_windows:
            if window.handle_event(event,window_offset=window_offset):
                return True
        return self.full.handle_event(event,window_offset=window_offset)

    def update(self,clock_time):
        #window offset is what I should subtract from mouse events to get the mouse position relative to this element
        if self.doing_activity is not None:
            if self.doing_activity.update(clock_time):
                #print("activite {} finished".format(type(self.doing_activity)))
                self.doing_activity=None
                if len(self.activity_deque)>0:
                    self.doing_activity=self.activity_deque.popleft()
                    self.doing_activity.start()
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
        cur_pos=self.engine.get_player().get_pos()
        new_pos=cur_pos+MapCoord.direction_to_vector(direction)
        #if there is a monster in the way, attack it
        objects=self.engine.level.map.get_objects_in_cell(new_pos)
        for object in objects:
            if isinstance(object,Entity):
                self.engine.set_player_action(MeleeAction(self.engine.get_player(),self.engine,object))
                return
        #if there is a door in the way, open it
        wall=self.engine.level.map.get_wall(cur_pos,direction)
        if wall is not None and wall.wall_type==WallType.DOOR_CLOSED:
            self.engine.set_player_action(OpenDoorAction(self.engine.get_player(),self.engine,wall.contents[0]))
            return

        self.engine.set_player_action(MoveAction(self.engine.get_player(),self.engine,direction))
        ...

    def handle_engine_message(self,message):
        self.mapview.handle_engine_message(message)
        self.statuspane.handle_engine_message(message)
        if message.message_type=="ObjectMoved":
            anim=MapAnimationMoveObject(self.mapview,self.engine,message.objid,message.oldpos,message.pos,100)
#            activity=GUIWaitForMapAnimation(self,self.engine,self.mapview.add_move_animation(message.objid,message.oldpos,message.pos,100))
            self.add_activity(GUIWaitForMapAnimation(self,self.engine,anim))
        if message.message_type=="InfoText":
            self.text_window.print(message.text)
        if message.message_type=="ActionFailed":
            self.text_window.print(message.reason)
        if message.message_type=="MeleeAttack":
            self.text_window.print(message.message)
            attacker=self.engine.level.object_store.get_object(message.attacker)
            defender=self.engine.level.object_store.get_object(message.defender)
            anim1=MapAnimationFlash(self.mapview,self.engine,defender.get_pos(),(255,0,0),200)
            anim2=MapAnimationNudgeObject(self.mapview,self.engine,message.attacker,attacker.get_pos(),defender.get_pos(),200)
            activity=GUIWaitForMapAnimation(self,self.engine,MapAnimationMultiple(self.mapview,self.engine,[anim1,anim2]))
            self.add_activity(activity)
        if message.message_type=="RangedAttack":
            self.text_window.print(message.message)
            speed=0.01
            dist=message.start_pos.manhattan_distance(message.end_pos)
            anim=MapAnimationMissile(self.mapview,self.engine,"arrow",message.start_pos,message.end_pos,dist/speed)
            activity=GUIWaitForMapAnimation(self,self.engine,anim)
            self.add_activity(activity)
            anim=MapAnimationFlash(self.mapview,self.engine,message.end_pos,(255,0,0))
            activity=GUIWaitForMapAnimation(self,self.engine,anim)
            self.add_activity(activity)
        if message.message_type=="CreatureDeath":
            ret=MapAnimationShakingSprite(self.mapview,self.engine,message.cell_pos,"skullnbones",500)
            self.add_activity(GUIWaitForMapAnimation(self,self.engine,self.mapview.add_animation(ret)))
            self.text_window.print("{} is defeated.".format(message.creature.reference_noun(specific=True)))
        if message.message_type=="RoomChanged":
            actor=self.engine.level.object_store.get_object(message.actor)
            if actor==self.engine.get_player():
                if message.message!="":
                    self.text_window.print(message.message)
            #self.text_window.print("{} moves to a new room.".format(actor.reference_noun()))
        if message.message_type=="ReadMessage":
            self.text_window.print("{}".format(message.text))
            self.add_popup_window(GUIInfoPopup(self.engine,self,message.text))

    def handle_cell_rightclick(self,event):
        print("cell rightclicked event")
#        cell=self.engine.level.map.get_cell(event.cell)
        objects=self.engine.level.map.get_objects_in_cell(event.cell)
        for obj in objects:
            if isinstance(obj,Entity):
                #if there's an enemy that I can melee, melee
                action=MeleeAction(self.engine.get_player(),self.engine,obj)
                if action.is_possible()[0]:
                    self.engine.set_player_action(action)
                    return
                #if there's an enemy that I can shoot, shoot
                action=RangedAttackAction(self.engine.get_player(),self.engine,obj)
                ranged_possible,reason=action.is_possible()
                if ranged_possible:
                    self.engine.set_player_action(action)
                    return
                else:
                    self.text_window.print(reason)
            else:
                #if there's an item, pick it up
                possible_actions=[TakeAction,ReadAction]
                for action_class in possible_actions:
                    action=action_class(self.engine.get_player(),self.engine,obj)
                    if action.is_possible()[0]:
                        self.engine.set_player_action(action)
                        return

#                action=TakeAction(self.engine.get_player(),self.engine,obj)
        #if there's a door, open it
        #if its an empty cell, try to move there
   

