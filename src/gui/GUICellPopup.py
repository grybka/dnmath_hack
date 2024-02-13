import pygame
import yaml
from ..gui_core.GUIElement import GUIElement, GUIHAnchor,GUIVAnchor

from ..gui_core.GUIPane import  GUIPane, GUIColLayout, GUIRowLayout

from ..gui_core.GUITextBox import GUITextBox, GUILabel
from ..gui_core.GUIButton import GUIButton,GUITextButtonCol,GUITextButtonRow
from .GUIItemPopup import GUIItemPopup
from ..actions.EntityAction import *
from . import GUIEvents

#this is a popup window that appears when you click on a cell
class GUICellPopup(GUIPane):
    def __init__(self,engine,mainwindow,cell_coord):
        self.engine=engine
        self.mainwindow=mainwindow
        self.cell_coord=cell_coord
        self.cell=engine.level.map.get_cell(cell_coord)
        #cell label
        self.cell_label=GUILabel("Cell: {},{}".format(cell_coord.x,cell_coord.y))
        #cell description
        self.cell_description=GUITextBox()
        text="Cell type: {}\n".format(self.cell.cell_type.name)
        text+="Ambient Light: {}\n".format(self.cell.ambient_light_level)
        text+="Lighting: {}\n".format(self.cell.light_level)
        self.cell_description.set_text(text)
        #possible actions
        doable_actions=self.evaluate_doable_actions()
        self.action_button_map={}
        for action in doable_actions:
            self.action_button_map[action.name]=action
        self.actions=GUITextButtonRow( (0,0,200,400), None,list(self.action_button_map.keys()),my_on_click=self.action_button_clicked,style_name="default_button")

        #objects
        objects=self.engine.level.map.get_objects_in_cell(self.cell_coord)
        self.item_button_map={}
        for obj in objects:
            self.item_button_map[obj.reference_noun()]=obj
        self.object_button_row=GUITextButtonRow( (0,0,200,400), None,list(self.item_button_map.keys()),my_on_click=self.item_button_clicked,style_name="default_button")

        #Cancel button
        self.cancel_button=GUIButton(GUILabel("Cancel",style_name="default_button"),None,on_click=self.cancel_button_clicked,style_name="default_button")
       
        #pane with items
#        self.items=GUITextButtonRow( 0,0,200,200),
        self.contents=GUIColLayout([self.cell_label,self.cell_description,self.actions,self.object_button_row,self.cancel_button],(0,0,300,400),element_proportions=[1,2,3,2,1],anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])
        super().__init__(self.contents,(0,0,400,400),my_style={"background_color":(0,0,0,200)})

    def cancel_button_clicked(self,mouse_button):
        self.mainwindow.remove_popup_window(self)

    def action_button_clicked(self,mouse_button,button):
        the_action=self.action_button_map[button]
        self.engine.set_player_action(the_action)
        self.mainwindow.remove_popup_window(self)

    def item_button_clicked(self,mouse_button,button):
        item=self.item_button_map[button]
        self.mainwindow.add_popup_window(GUIItemPopup(self.engine,self.mainwindow,item))
        self.mainwindow.remove_popup_window(self)

    def evaluate_doable_actions(self):
        return []