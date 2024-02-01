import pygame
import yaml
from ..gui_core.GUIElement import GUIElement, GUIHAnchor,GUIVAnchor

from ..gui_core.GUIPane import  GUIPane, GUIColLayout, GUIRowLayout

from ..gui_core.GUITextBox import GUITextBox, GUILabel
from ..gui_core.GUIButton import GUIButton,GUITextButtonCol,GUITextButtonRow
from ..actions.EntityAction import *
from . import GUIEvents

#this is a popup window that appears when you click on an item in the inventory
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
        #Cancel button
        self.cancel_button=GUIButton(GUILabel("Cancel",style_name="default_button"),None,on_click=self.cancel_button_clicked,style_name="default_button")
        #item label
        self.item_label=GUILabel(item.reference_noun(specific=False))
        #panel with options
        self.inventory=GUITextButtonRow( (0,0,200,400), None,list(self.action_button_map.keys()),my_on_click=self.inventory_button_clicked,style_name="default_button")
        self.contents=GUIColLayout([self.item_label,self.inventory,self.cancel_button],(0,0,300,400),element_proportions=[1,1,1],anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])
        super().__init__(self.contents,(0,0,300,400),my_style={"background_color":(0,0,0,200)})

    def eveluate_dodable_actions(self):
        doable_actions=[]
        for action_class in [DropAction,EquipAction, UnequipAction]:
            action=action_class(self.engine.get_player(),self.engine,self.item)
            if action.is_possible()[0]:
                doable_actions.append(action)
        return doable_actions

    def cancel_button_clicked(self):
        self.mainwindow.remove_popup_window(self)
    
    def inventory_button_clicked(self,button):
        print("{} clicked".format(button))
        the_action=self.action_button_map[button]
        self.engine.set_player_action(the_action)
        self.mainwindow.remove_popup_window(self)
