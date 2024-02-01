import pygame
from .GUIElement import GUIElement,GUIHAnchor,GUIVAnchor
from .GUIPane import GUIPane
from collections import deque

#This is a single line of text
class GUILabel(GUIElement):
    def __init__(self,text,my_style={},anchors=(GUIHAnchor.CENTER,GUIVAnchor.CENTER),rect=(0,0,0,0),style_name="default"):
        super().__init__(my_style,rect=rect,style_name=style_name)
        self.h_anchor=anchors[0]
        self.v_anchor=anchors[1]
        self.set_text(text)

    def update_style(self,style):
        super().update_style(style)
        self.text_size=self.get_style_value("label_text_size",24)
        self.text_color=self.get_style_value("label_text_color",(255,255,255))
        self.font = pygame.font.SysFont("Courier", self.text_size)

    def draw_screen(self,surf):
        if not super().draw_screen(surf):
            return False
        x0=self.rect[0]
        y0=self.rect[1]
        if self.h_anchor==GUIHAnchor.CENTER:
            x0=self.rect[0]+(self.rect[2]-self.text_surf.get_width())/2
        elif self.h_anchor==GUIHAnchor.RIGHT:
            x0=self.rect[0]+self.rect[2]-self.text_surf.get_width()
        if self.v_anchor==GUIVAnchor.CENTER:
            y0=self.rect[1]+(self.rect[3]-self.text_surf.get_height())/2
        elif self.v_anchor==GUIVAnchor.BOTTOM:
            y0=self.rect[1]+self.rect[3]-self.text_surf.get_height()
        surf.blit(self.text_surf,(x0,y0))
        return True
    
    def get_width(self):
        return self.text_surf.get_width()
    
    def get_height(self):
        return self.text_surf.get_height()

    def set_text(self,text):
        self.text=text
        self.text_surf=self.font.render(self.text, True, self.text_color)
        self.rect=(self.rect[0],self.rect[1],self.text_surf.get_width(),self.text_surf.get_height())
        self.a_redraw_is_needed()

#This is a multiline text box
class GUITextBox(GUIElement):
    def __init__(self,rect=(0,0,0,0),my_style={},anchors=(GUIHAnchor.CENTER,GUIVAnchor.CENTER)):
        super().__init__(my_style,rect=rect)
        self.h_anchor=anchors[0]
        self.v_anchor=anchors[1]
        self.font = pygame.font.SysFont("Courier", 24)
        self.max_lines=20
        self.text_lines=deque([],self.max_lines)
        
    def update_style(self,style):
        super().update_style(style)
        self.text_size=self.get_style_value("text_size",24)

    def draw_screen(self,surf):
        if not super().draw_screen(surf):
            return False
        surf.fill((0,0,0))
        line_surfs=[]
        total_height=0
        max_width=0
        for line in self.text_lines:
            line_surfs.append(self.font.render(line, True, (255,255,255)))
            total_height+=line_surfs[-1].get_height()
            if line_surfs[-1].get_width()>max_width:
                max_width=line_surfs[-1].get_width()
        x0=0
        y0=0
        if self.h_anchor==GUIHAnchor.CENTER:
            x0=(surf.get_width()-max_width)/2
        elif self.h_anchor==GUIHAnchor.RIGHT:
            x0=surf.get_width()-max_width
        if self.v_anchor==GUIVAnchor.CENTER:
            y0=(surf.get_height()-total_height)/2
        elif self.v_anchor==GUIVAnchor.BOTTOM:
            y0=surf.get_height()-total_height
        for line_surf in line_surfs:
            surf.blit(line_surf,(x0,y0))
            y0+=line_surf.get_height()
        self.redraw_needed=False

  
    def add_line(self,text):
        self.text_lines.append(text)
        self.a_redraw_is_needed()

    def clear(self):
        self.text_lines.clear()
        self.a_redraw_is_needed()
    
    def print(self,text):
        for line in text.split("\n"):
            self.add_line(line)
        self.a_redraw_is_needed()

    def backspace(self):
        if len(self.text_lines)<=0:
            return
        if len(self.text_lines[0])<=0:
            return
        self.text_lines[0]=self.text_lines[0][:-1]
        self.a_redraw_is_needed()
    
    def add_text_to_line(self,text):
        if len(self.text_lines)<=0:
            self.text_lines.append(text)
        else:
            self.text_lines[0]+=text
        self.a_redraw_is_needed()

    def get_last_line(self):
        if len(self.text_lines)<=0:
            return ""
        return self.text_lines[-1]
    
    def set_text(self,text):
        self.text_lines.clear()
        for line in text.split("\n"):
            self.text_lines.append(line)
        self.a_redraw_is_needed()