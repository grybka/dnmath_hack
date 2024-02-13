import pygame
import yaml
from ..gui_core.GUIElement import GUIElement, GUIHAnchor,GUIVAnchor

from ..gui_core.GUIPane import  GUIPane, GUIColLayout, GUIRowLayout

from ..gui_core.GUITextBox import GUITextBox, GUILabel
from ..gui_core.GUIButton import GUIButton,GUITextButtonCol,GUITextButtonRow
from .GUIContainerPopup import GUIContainerPopup
from ..actions.EntityAction import *
from . import GUIEvents

#this is a popup window that appears when you click on an item
#TODO have a way for it to updated when the item changes
class GUIItemPopup(GUIPane):
    def __init__(self,engine,mainwindow,item):
        self.engine=engine
        self.mainwindow=mainwindow
        self.item=item
        #possible actions
        doable_actions=self.eveluate_dodable_actions()
        self.action_button_map={}
        for action in doable_actions:
            self.action_button_map[action.name]=action
        #special cases
        if isinstance(item,GameObjectContainer) and not item.closed_not_open:
            self.action_button_map["Loot"]=None
        if isinstance(item,GameObjectContainer) and not item.closed_not_open:
            self.action_button_map["Fill"]=None

        #Cancel button
        self.cancel_button=GUIButton(GUILabel("Cancel",style_name="default_button"),None,on_click=self.cancel_button_clicked,style_name="default_button")
        #item label
        self.item_label=GUILabel(item.reference_noun(specific=False))
        #panel with options
        self.inventory=GUITextButtonRow( (0,0,200,400), None,list(self.action_button_map.keys()),my_on_click=self.inventory_button_clicked,style_name="default_button")
        self.contents=GUIColLayout([self.item_label,self.inventory,self.cancel_button],(0,0,300,400),element_proportions=[1,5,1],anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])
        super().__init__(self.contents,(0,0,400,400),my_style={"background_color":(0,0,0,200)})

    def eveluate_dodable_actions(self):
        doable_actions=[]
        for action_class in [TakeAction, DropAction,EquipAction, UnequipAction, MeleeAction, RangedAttackAction, ReadAction, OpenDoorAction, CloseDoorAction, OpenContainerAction, CloseContainerAction]:
            action=action_class(self.engine.get_player(),self.engine,self.item)
            if action.is_possible()[0]:
                doable_actions.append(action)
        return doable_actions

    def cancel_button_clicked(self,mouse_button):
        self.mainwindow.remove_popup_window(self)
    
    def inventory_button_clicked(self,mouse_button,button):
        the_action=self.action_button_map[button]
        if the_action is None:
            if button=="Loot":
                self.mainwindow.add_popup_window(GUIContainerPopup(self.engine,self.mainwindow,self.item.contents,self.item,False))
            elif button=="Fill":
                self.mainwindow.add_popup_window(GUIContainerPopup(self.engine,self.mainwindow,self.engine.get_player().inventory,self.item,True))
        else:
            self.engine.set_player_action(the_action)
        #some actions leave the window open for convenience
        self.mainwindow.remove_popup_window(self)