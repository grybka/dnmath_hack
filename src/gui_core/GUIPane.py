import pygame
from collections import deque
from .GUIElement import GUIElement, GUIHAnchor,GUIVAnchor

#TODO, redo these to handle the anchor resize

#This is a (possibly bordered) box that contains exacly one other GUIElement
class GUIPane(GUIElement):
    def __init__(self,element,rect,my_style={},anchors=(GUIHAnchor.RESIZE,GUIVAnchor.RESIZE)):
        #rect is (x1,y1,w,h)
        self.element=element
        self.anchors=anchors
        super().__init__(my_style,rect=rect)
        self.content_rect=rect
        self.set_element(element)
#        if element:
#            element.set_container(self)

    def handle_event(self,event,window_offset=(0,0)):
        if self.element:
            return self.element.handle_event(event,window_offset=(self.content_rect[0],self.content_rect[1]))
        return False

    def update(self,clock_time):
        if self.element:
            self.element.update(clock_time)

    def update_style(self,style={}):
        super().update_style(style)
        self.border_color=self.get_gui_color(self.get_style_value("border_color",(0,0,0)))
        self.border_radius=self.get_style_value("border_radius",0)
        self.bg_color=self.get_gui_color(self.get_style_value("bg_color",(0,0,0)))
        self.margin=self.get_style_value("margin",0) #area between the edge of the surface and the border
        self.border_width=self.get_style_value("border_width",0) #width of the border
        self.padding=self.get_style_value("padding",0) #area between the border and the element
        self.a_resize_is_needed()

    def draw_screen(self,surf):
        if not super().draw_screen(surf):
            return False
        self.draw_border(surf.subsurface( self.rect ) )
        if self.element:
            self.element.a_redraw_is_needed()
            self.element.draw_screen(surf.subsurface( self.content_rect))
        return True
    
    def is_a_redraw_needed(self):
        if super().is_a_redraw_needed():
            return True
        if self.element:
            return self.element.is_a_redraw_needed()

    def draw_border(self,surf):
        #clear the screen with bg color
        pygame.draw.rect(surf,self.bg_color,(0,0,surf.get_width(),surf.get_height()))
        #draw border if necessary
        if self.border_width>0:
            pygame.draw.rect(surf,self.border_color,(self.margin,self.margin,surf.get_width()-2*self.margin,surf.get_height()-2*self.margin),self.border_width,self.border_radius)

    def resize(self,rect=None):
        super().resize(rect)
        rect=self.rect
        total_padding=self.margin+self.border_width+self.padding
        self.content_rect=(rect[0]+total_padding,rect[1]+total_padding,rect[2]-2*total_padding,rect[3]-2*total_padding)
        if self.element:
            #here is where my anchors matter
            element_rect=[0,0,0,0]
            if self.anchors[0]==GUIHAnchor.LEFT:
                element_rect[0]=0
                element_rect[2]=self.element.get_width()
            elif self.anchors[0]==GUIHAnchor.CENTER:
                element_rect[0]=(self.content_rect[2]-self.element.get_width())/2
                element_rect[2]=self.element.get_width()
            elif self.anchors[0]==GUIHAnchor.RIGHT:
                element_rect[0]=self.content_rect[2]-self.element.get_width()
                element_rect[2]=self.element.get_width()
            elif self.anchors[0]==GUIHAnchor.RESIZE:
                element_rect[0]=0
                element_rect[2]=self.content_rect[2]

            if self.anchors[1]==GUIVAnchor.TOP:
                element_rect[1]=0
                element_rect[3]=self.element.get_height()
            elif self.anchors[1]==GUIVAnchor.CENTER:
                element_rect[1]=(self.content_rect[3]-self.element.get_height())/2
                element_rect[3]=self.element.get_height()
            elif self.anchors[1]==GUIVAnchor.BOTTOM:
                element_rect[1]=self.content_rect[3]-self.element.get_height()
                element_rect[3]=self.element.get_height()
            elif self.anchors[1]==GUIVAnchor.RESIZE:
                element_rect[1]=0
                element_rect[3]=self.content_rect[3]
            self.element.resize(element_rect)

    def set_element(self,element):
        self.element=element
        if element is not None:
            element.set_container(self)
        self.a_resize_is_needed()
        self.a_redraw_is_needed()

    def __str__(self):
        return "GUIPane "+str(self.rect)+" contains "+str(self.element)

class GUIMultiContainer(GUIElement):
    def __init__(self,elements=[],my_style={},rect=(0,0,0,0),style_name="default"):
        self.elements=elements
        for element in self.elements:
            element.set_container(self)
        super().__init__(my_style,rect=rect,style_name=style_name)

    def add_element(self,element):
        self.elements.append(element)
        element.set_container(self)
        self.a_resize_is_needed()

    def update_style(self,style):
        super().update_style(style)
        for element in self.elements:
            element.update_style(style)

    def handle_event(self,event,window_offset=(0,0)):
        for element in self.elements:
            if element.handle_event(event,window_offset):
                return True
        return False
    
    def update(self,clock_time):
        for element in self.elements:
            element.update(clock_time)

    def draw_screen(self,surf):
        if not super().draw_screen(surf):
            return False
        #clear the screen with bg color
        #pygame.draw.rect(surf,self.bg_color,(0,0,surf.get_width(),surf.get_height()))
        for element in self.elements:
            #if I had to redraw, everything beneath me has to redraw
            element.a_redraw_is_needed()
            element.draw_screen(surf)
        return True
    
    def is_a_redraw_needed(self):
        if super().is_a_redraw_needed():
            return True
        for element in self.elements:
            if element.is_a_redraw_needed():
                return True
        return False
    
    def clear_contents(self):
        self.elements=[]
    #always override resize

class GUIRowLayout(GUIMultiContainer):
    def __init__(self,elements,rect,my_style={},anchors=(GUIHAnchor.RESIZE,GUIVAnchor.RESIZE),element_proportions=None,style_name="default"):
        self.anchor=anchors
        super().__init__(elements,my_style,rect,style_name=style_name)
        self.element_proportions=element_proportions #only for resize
        if self.element_proportions is None:
            self.element_proportions=[1]*len(self.elements)
        
    def add_element(self,element,proportion=1):
        super().add_element(element)       
        self.element_proportions.append(proportion)

    def clear_contents(self):
        super().clear_contents()
        self.element_proportions=[]

    def update_style(self,style):
        super().update_style(style)
        self.element_padding=self.get_style_value("element_padding",0)

    def resize(self,rect=None):
        super().resize(rect)
        rect=self.rect
        total_padding=self.element_padding*(len(self.element_proportions)+1)
        if len(self.elements)==0:
            return
        element_rects=[ [0,0,0,0] for element in self.elements ]
        total_width=sum([element.get_width() for element in self.elements])+(len(self.elements)+1)*self.element_padding
        total_height=max([element.get_height() for element in self.elements])+2*self.element_padding
        if self.anchor[0]==GUIHAnchor.RESIZE:
            hsize=(rect[2]-total_padding)/sum(self.element_proportions)
            on_x=rect[0]+self.element_padding
            for i in range(len(self.elements)):
                width=int(hsize*self.element_proportions[i])
                element_rects[i][0]=on_x
                element_rects[i][2]=width                
                on_x=on_x+width+self.element_padding
        else:
            x0=rect[0]+self.element_padding
            if self.anchor[0]==GUIHAnchor.CENTER:
                x0=rect[0]+(rect[2]-total_width)//2
            elif self.anchor[0]==GUIHAnchor.RIGHT:
                x0=rect[0]+rect[2]-total_width
            for i in range(len(self.elements)):
                element_rects[i][0]=x0
                element_rects[i][2]=self.elements[i].get_width()
                x0+=self.elements[i].get_width()+self.element_padding
        if self.anchor[1]==GUIVAnchor.RESIZE:
            for i in range(len(self.elements)):
                element_rects[i][1]=rect[1]+self.element_padding
                element_rects[i][3]=rect[3]-2*self.element_padding
        else:
            y0=rect[1]+self.element_padding
            if self.anchor[1]==GUIVAnchor.CENTER:
                y0=rect[1]+(rect[3]-total_height)//2
            elif self.anchor[1]==GUIVAnchor.BOTTOM:
                y0=rect[1]+rect[3]-total_height
            for i in range(len(self.elements)):
                element_rects[i][1]=y0
                element_rects[i][3]=self.elements[i].get_height()
                #y0+=self.elements[i].get_height()+self.element_padding   
        #print("MY RECT {}".format(self.rect))
        #print("ANCHORS {}".format(self.anchor))
        #print("ELEMENTS: {}".format(element_rects)) 
        for i in range(len(self.elements)):
            self.elements[i].resize(element_rects[i])

class GUIColLayout(GUIMultiContainer):
    def __init__(self,elements,rect=(0,0,0,0),my_style={},anchors=(GUIHAnchor.RESIZE,GUIVAnchor.RESIZE),element_proportions=None,style_name="default"):
        self.anchor=anchors
        super().__init__(elements,my_style,rect,style_name=style_name)
        self.element_proportions=element_proportions #only for resize
        if self.element_proportions is None:
            self.element_proportions=[1]*len(self.elements)

    def add_element(self,element,proportion=1):
        super().add_element(element)       
        self.element_proportions.append(proportion)

    def draw_screen(self,surf):
        super().draw_screen(surf)
        #pygame.draw.rect(surf,(255,0,0),self.rect,1)


    def clear_contents(self):
        super().clear_contents()
        self.element_proportions=[]

    def update_style(self,style):
        super().update_style(style)
        self.element_padding=self.get_style_value("element_padding",0)

    def resize(self,rect=None):
        super().resize(rect)
        rect=self.rect
        total_padding=self.element_padding*(len(self.element_proportions)+1)
        if len(self.elements)==0:
            return
        element_rects=[ [0,0,0,0] for element in self.elements ]
        total_height=sum([element.get_height() for element in self.elements])+(len(self.elements)+1)*self.element_padding
        total_width=max([element.get_width() for element in self.elements])+2*self.element_padding
        if self.anchor[1]==GUIVAnchor.RESIZE:
            vsize=(rect[3]-total_padding)/sum(self.element_proportions)
            on_y=rect[1]+self.element_padding
            for i in range(len(self.elements)):
                height=int(vsize*self.element_proportions[i])
                element_rects[i][1]=on_y
                element_rects[i][3]=int(height)
                on_y=on_y+height+self.element_padding
        else:
            y0=rect[1]+self.element_padding
            if self.anchor[1]==GUIVAnchor.CENTER:
                y0=rect[1]+(rect[3]-total_height)//2
            elif self.anchor[1]==GUIVAnchor.BOTTOM:
                y0=rect[1]+rect[3]-total_height
            for i in range(len(self.elements)):
                element_rects[i][1]=y0
                element_rects[i][3]=self.elements[i].get_height()
                y0+=self.elements[i].get_height()+self.element_padding
        if self.anchor[0]==GUIHAnchor.RESIZE:
            for i in range(len(self.elements)):
                element_rects[i][0]=rect[0]+self.element_padding
                element_rects[i][2]=rect[2]-2*self.element_padding
        else:
            x0=rect[0]+self.element_padding
            if self.anchor[0]==GUIHAnchor.CENTER:
                x0=rect[0]+(rect[2]-total_width)//2
            elif self.anchor[0]==GUIHAnchor.RIGHT:
                x0=rect[0]+rect[2]-total_width
            for i in range(len(self.elements)):
                element_rects[i][0]=x0
                element_rects[i][2]=self.elements[i].get_width()
                #x0+=self.elements[i].get_width()+self.element_padding
        for i in range(len(self.elements)):
            self.elements[i].resize(element_rects[i])

