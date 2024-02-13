#This is a list of items, eitehr in a container or inventory

import pygame
import yaml
from ..gui_core.GUIElement import GUIElement, GUIHAnchor,GUIVAnchor

from ..gui_core.GUIPane import  GUIPane, GUIColLayout, GUIRowLayout

from ..gui_core.GUITextBox import GUITextBox, GUILabel
from ..gui_core.GUIButton import GUIButton,GUITextButtonCol,GUITextButtonRow
from ..actions.EntityAction import *
from . import GUIEvents

class GUIContainerPopup(GUIPane):
    def __init__(self,engine,mainwindow,item_list,container,in_not_out=True):
        self.engine=engine
        self.mainwindow=mainwindow
        self.item_list=item_list
        self.in_not_out=in_not_out
        self.looting_container=container
        
        #Cancel button
        self.cancel_button=GUIButton(GUILabel("Cancel",style_name="default_button"),None,on_click=self.cancel_button_clicked,style_name="default_button")
        #item label
        if in_not_out:
            self.item_label=GUILabel("Select an item to put in")
        else:
            self.item_label=GUILabel("Select an item to take")

        self.button_map={}
        for item in item_list:
            self.button_map[item.reference_noun()]=item
        #panel with options
        self.inventory=GUITextButtonRow( (0,0,200,400), None,list(self.button_map.keys()),my_on_click=self.item_button_clicked,style_name="default_button")
        self.contents=GUIColLayout([self.item_label,self.inventory,self.cancel_button],(0,0,300,400),element_proportions=[1,5,1],anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])
        super().__init__(self.contents,(0,0,400,400),my_style={"background_color":(0,0,0,200)})

    def cancel_button_clicked(self,mouse_button):
        self.mainwindow.remove_popup_window(self)

    def item_button_clicked(self,mouse_button,button):
        item=self.button_map[button]
        #if it's coming out of a container, a container, clicking on the item takes it
        #if its going in, clicking on the item puts it in
        if not self.in_not_out:
            action=LootAction(self.engine.get_player(),self.engine,self.looting_container,item)
            self.engine.set_player_action(action)
        else:
            action=InsertAction(self.engine.get_player(),self.engine,self.looting_container,item)
            self.engine.set_player_action(action)


        #self.mainwindow.add_popup_window(GUIItemPopup(self.engine,self.mainwindow,item))
        self.mainwindow.remove_popup_window(self)
