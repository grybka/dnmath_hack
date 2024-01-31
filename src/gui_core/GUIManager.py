import yaml
from .GUIElement import GUIElement
from .GUIStyle import get_gui_style,set_gui_style

def recursive_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = recursive_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

class GUIManager:
    def __init__(self,screen_size):
        self.screen_size=screen_size
        #these are the GUIElements that live at the top level.  They may contain others
        self.top_elements=[]
        self.default_gui_style={"colors":{}, "defaults":{}}


    def handle_event(self,event):
        for element in self.top_elements:
            element.handle_event(event)

    def update(self,clock_time):
        for element in self.top_elements:
            element.update(clock_time)

    def draw_screen(self,surf):
        for element in self.top_elements:
            element.draw_screen(surf)

    def load_style_file(self,fname):
        with open(fname, 'r') as file:
            self.default_gui_style = yaml.safe_load(file)
            set_gui_style(self.default_gui_style)
            #default_gui_style = yaml.safe_load(file)
            #file.close()

    def update_style_with_file(self,fname):
        with open(fname, 'r') as file:
            style_addition=yaml.safe_load(file)
            print("style addition",style_addition)
            recursive_update(self.default_gui_style,style_addition)
            #file.close()

    def get_default_gui_style(self):
        return self.default_gui_style["defaults"]
    
    def get_gui_colors(self):
        if "colors" in self.default_gui_style:
            return self.default_gui_style["colors"]
        return {}

    def add_element(self,element):
        element.set_container(self)
        self.top_elements.append(element)