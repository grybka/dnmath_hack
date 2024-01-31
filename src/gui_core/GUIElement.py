import pygame
from enum import Enum
from .GUIStyle import get_gui_style

class GUIHAnchor(Enum):
    LEFT=0
    CENTER=1
    RIGHT=2
    RESIZE=3

class GUIVAnchor(Enum):
    TOP=0
    CENTER=1
    BOTTOM=2
    RESIZE=3

def point_in_rect(point,rect):
    return point[0]>=rect[0] and point[0]<rect[0]+rect[2] and point[1]>=rect[1] and point[1]<rect[1]+rect[3]

def clip_rect(rect,clip_rect):
    x0=max(rect[0],clip_rect[0])
    y0=max(rect[1],clip_rect[1])
    x1=min(rect[0]+rect[2],clip_rect[0]+clip_rect[2])
    y1=min(rect[1]+rect[3],clip_rect[1]+clip_rect[3])
    return (x0,y0,x1-x0,y1-y0)

class GUIElement:
    def __init__(self,my_style={},style_name="default",rect=(0,0,0,0),container=None):
        self.my_gui_style={}
        self.container=container
        self.rect=rect #This is where I am allowed to draw on the screen I will be given
        self.style_name=style_name
        self._redraw_needed=True
        self._resize_needed=True
        self.update_style(my_style)
        ...

    #returns true if this event had an effect on this element
    def handle_event(self,event,window_offset=(0,0)):
        return False

    #tells the eleent that time has passed
    def update(self,clock_time):
        #window offset is what I should subtract from mouse events to get the mouse position relative to this element
        ...

    #draws this element onto the given surface
    #returns true if this element or any element it contains needs to be redrawn
    def draw_screen(self,surf):
        if self.is_a_resize_needed():
            self.resize()
        if self.is_a_redraw_needed():
            self._redraw_needed=False
            return True
        return False
    
    #called right before a redraw
    def resize(self,rect=None):
        if rect is not None:
            if len(rect)!=4:
                raise Exception("Rect must have 4 elements")
            self.rect=(rect[0],rect[1],max(rect[2],0),max(rect[3],0))
        self._resize_needed=False
        self.a_redraw_is_needed()

    #updates the local style of this element
    def update_style(self,style={}):
        if not isinstance(style,dict):
            raise Exception("Style must be a dictionary, its {}".format(style))
        self.my_gui_style.update(style)
        self._redraw_needed=True

    #return true if this element or any element it contains needs to be redrawn
    def is_a_redraw_needed(self):
        return self._redraw_needed
    
    def a_redraw_is_needed(self):
        self._redraw_needed=True

    def is_a_resize_needed(self):
        return self._resize_needed
    
    def a_resize_is_needed(self):
        self._resize_needed=True

    def set_container(self,container):
        self.container=container

    def get_style_value(self,key,default=None):
        gui_style=get_gui_style()
        if key in self.my_gui_style:
            return self.my_gui_style[key]
        elif key in gui_style[self.style_name]:
            return gui_style[self.style_name][key]
        return default

    def get_default_gui_style(self):
        ret=get_gui_style()
        return ret

    def get_gui_colors(self):
        return self.get_default_gui_style()["colors"]

    def get_gui_color(self,key,default=(0,0,0)):
        if isinstance(key,tuple):
            return key
        if key in self.my_gui_style:
            return self.get_gui_color(self.my_gui_style[key])
        elif key in self.get_gui_colors():
            return self.get_gui_colors()[key]
        raise Exception("Color "+str(key)+" not found in style")
    
    def set_x(self,x):
        self.rect=(x,self.rect[1],self.rect[2],self.rect[3])
        self.a_resize_is_needed()

    def set_y(self,y):
        self.rect=(self.rect[0],y,self.rect[2],self.rect[3])
        self.a_resize_is_needed()
        
    def get_width(self):
        return self.rect[2]
    
    def get_height(self):
        return self.rect[3]

    def __str__(self):
        return "GUIElement at "+str(self.rect)

    def diagnose(self):
        return "GUIElement at {}".format(self.rect)