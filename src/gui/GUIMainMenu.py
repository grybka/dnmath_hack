from ..gui_core.GUIElement import GUIElement,point_in_rect,GUIHAnchor,GUIVAnchor
from ..gui_core.GUITextBox import GUILabel
from ..gui_core.GUIPane import GUIPane, GUIColLayout
from ..gui_core.GUIButton import GUITextButtonPanel, GUITextButtonRow
from . import GUIEvents
from ..actions.EntityAction import *

#This is a label followed by a button menu
class GMMMenu(GUIColLayout):
    def __init__(self,label_text,rect):
        self.label=GUILabel(label_text,my_style={"label_text_color":(255,255,255),"label_text_size":20})
        button_rect=[0,0,120,50]
        self.menu=GUITextButtonRow(rect,button_rect,[],my_on_click=self.button_clicked,style_name="default_button")
        super().__init__([self.label,self.menu],rect,anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP))
        for i in range(len(self.elements)):
            print("GMMenu element {}".format(self.elements[i].rect))

    def button_clicked(self,text):
        print("button clicked {}".format(text))
        self.on_click(text)


class GMMCellMenu(GMMMenu):
    def __init__(self,engine,rect,cell):
        label_text="Cell: {},{}".format(cell.x,cell.y)
        super().__init__(label_text,rect)
        self.engine=engine
        self.cell=cell
#        self.menu.add_button("Move")
        self.resize(rect)

    def on_click(self,text):
        ...

class GMMObjectMenu(GMMMenu):
    def __init__(self,engine,rect,object):
        label_text="{}".format(object.reference_noun(specific=False))
        super().__init__(label_text,rect)
        self.engine=engine
        self.object=object
        self.menu.add_button("Take")
        if isinstance(object,Entity):
            self.menu.add_button("Ranged Attack")
        self.resize(rect)

    def on_click(self,text):
        print("GMMObjectMenu on_clic {}".format(text))
        if text=="Take":
            print("taking action")
            self.engine.set_player_action(TakeAction(self.engine.get_player(),self.engine,self.object))
        if text=="Ranged Attack":
            print("ranged attack action")
            self.engine.set_player_action(RangedAttackAction(self.engine.get_player(),self.engine,self.object))
        ...


class GUIMainMenu(GUIColLayout):
    def __init__(self,engine,rect):
        super().__init__([],rect,anchors=(GUIHAnchor.RESIZE,GUIVAnchor.TOP))
        self.engine=engine

    def handle_event(self,event,window_offset=(0,0)):
        if event.type == GUIEvents.CELL_SELECTED_EVENT:
            if event.cell is None:
                ...
            else:
                ...
                #self.cell_selected_menu(event.cell)

        return super().handle_event(event,window_offset=window_offset)

    def cell_selected_menu(self,cell):
        self.container.redraw_needed=True
        self.redraw_needed=True
        self.clear_contents()
        if cell is None:
            return 
        self.add_element(GMMCellMenu(self.engine,(0,0,self.rect[2],100),cell),[0,0,self.rect[2],100])
        objects=self.engine.level.map.get_objects_in_cell(cell)
        for object in objects:
            self.add_element(GMMObjectMenu(self.engine,(0,0,self.rect[2],100),object),[0,0,self.rect[2],100])
        self.resize(self.rect)
        #print('cell selected menu')
