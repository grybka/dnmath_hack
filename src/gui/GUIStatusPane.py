import pygame
import yaml
from ..gui_core.GUIElement import GUIElement, GUIHAnchor,GUIVAnchor
from ..gui_core.GUIPane import  GUIPane, GUIColLayout, GUIRowLayout
from ..gui_core.GUITextBox import GUITextBox, GUILabel
from ..gui_core.GUIButton import GUITextButtonCol
from .GUIItemPopup import GUIItemPopup
from . import GUIEvents
from ..actions.EntityAction import *

#Information to be displayed in the status pane
#Your health
#your inventory (clickable buttons)


class GUIStatusPane(GUIColLayout):
    def __init__(self,engine,mainwindow):
        self.engine=engine
        self.mainwindow=mainwindow
        self.button_rect=None
        self.health_info=GUILabel("Health: 100/100",anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP))
        #self.health_info=GUITextBox()
        player=self.engine.get_player()

        button_names=[]

        equipment_label=GUILabel("Equipped",anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP))
        inventory_label=GUILabel("Inventory",anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP))
        self.equipped_list=GUITextButtonCol( (0,0,200,400), self.button_rect,button_names,my_on_click=self.equip_button_clicked,style_name="inventory_button",anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP))
        self.inventory=GUITextButtonCol( (0,0,200,400), self.button_rect,button_names,my_on_click=self.inventory_button_clicked,style_name="inventory_button",anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP))
        equipment_panel=GUIColLayout([equipment_label,self.equipped_list],(0,0,200,400),anchors=[GUIHAnchor.LEFT,GUIVAnchor.TOP])
        inventory_panel=GUIColLayout([inventory_label,self.inventory],(0,0,200,400),anchors=[GUIHAnchor.LEFT,GUIVAnchor.TOP])


        self.item_rows=GUIRowLayout([equipment_panel,inventory_panel],(0,0,200,400),element_proportions=[1,1],anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])

        self.update_status()


        super().__init__([self.health_info,self.item_rows])

    def handle_event(self,event,window_offset=(0,0)):
        if event.type == GUIEvents.CELL_SELECTED_EVENT:
            if event.cell is None:
                text=""
            else:
                text="Cell selected:\n {}".format(event.cell)
                for wall in self.engine.level.map.get_cell(event.cell).walls:
                    text+="\n{}".format(wall)
        super().handle_event(event,window_offset)

    def handle_engine_message(self,message):
        update_messages=["PlayerInventoryChanged","PlayerEquippedChanged","MeleeAttack","RangedAttack"]
        if message.message_type in update_messages:
            self.update_status()

    def update_status(self):
        player=self.engine.get_player()

        self.health_info.set_text("Health: {}/{}".format(player.hp,player.max_hp))
        #self.inventory.set_text("Inventory:\n{}".format("\n".join([item.reference_noun(specific=False) for item in player.inventory])))
        #self.add_element(self.inventory)
        self.equipped_list.clear_contents()
        self.inventory.clear_contents()

        button_names=[]
        equipped_button_names=[]
        self.inventory_button_map={}
        self.equipment_button_map={}
        for slot in player.equip_slots:
            equipped_item=player.get_equipped_item(slot)
            if equipped_item is None:
                text="{}: {}".format(slot,"Nothing")
                equipped_button_names.append(text)
                self.equipment_button_map[text]=None
            else:
                name=equipped_item.reference_noun(specific=False)
                text="{}: {}".format(slot,name)
                self.equipment_button_map[text]=equipped_item
                equipped_button_names.append(text)
        for item in player.inventory:
            name=item.reference_noun(specific=False)
            self.inventory_button_map[name]=item
            button_names.append(name)

        #button_names=[item.reference_noun(specific=False) for item in player.inventory]
        for button in button_names:
            print("adding button {}".format(button))
            self.inventory.add_button(button)
        for button in equipped_button_names:
            print("adding equipped button {}".format(button))
            self.equipped_list.add_button(button)

        self.a_redraw_is_needed()

    def inventory_button_clicked(self,mouse_button,text):
        print("inventory button clicked {}".format(text))
        if mouse_button==1:
            self.mainwindow.add_popup_window(GUIItemPopup(self.engine,self.mainwindow,self.inventory_button_map[text]))
        elif mouse_button==3:
            print("right clicked")
            #if I can wear it, wear it
            action=EquipAction(self.engine.get_player(),self.engine,self.inventory_button_map[text])
            possibility=action.is_possible()
            if possibility[0]:
                self.engine.set_player_action(action)
            else:
                self.mainwindow.text_window.print(possibility[1])
            #TODO if I can use it or drink it or eat it, use it
        else:
            print("unhandleded mouse button {}".format(mouse_button))

    def equip_button_clicked(self,mouse_button,text):
        print("equip button clicked {}".format(text))
        obj=self.equipment_button_map[text]
        if obj is not None:
            if mouse_button==1:
                self.mainwindow.add_popup_window(GUIItemPopup(self.engine,self.mainwindow,obj))
            else:
                action=UnequipAction(self.engine.get_player(),self.engine,obj)
                possibility=action.is_possible()
                if possibility[0]:
                    self.engine.set_player_action(action)
                else:
                    self.mainwindow.text_message(possibility[1])
