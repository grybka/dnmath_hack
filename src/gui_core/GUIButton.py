import pygame
from enum import Enum
from .GUIElement import GUIElement, point_in_rect, GUIHAnchor,GUIVAnchor, clip_rect
from .GUIPane import GUIRowLayout, GUIColLayout
from .GUITextBox import GUILabel
class GUIButtonState(Enum):
    NORMAL=0
    HOVERED=1
    CLICKED=2
    DISABLED=3

class GUIButton(GUIElement):
    def __init__(self,element,rect=None,my_style={},is_disabled=False,on_click=None,style_name="default"):
        self.element=element
        self.redraw_needed=True
        self.is_disabled=is_disabled
        self.on_click=on_click
        super().__init__(my_style,rect=rect,style_name=style_name)
        if is_disabled:
            self.state=GUIButtonState.DISABLED
        else:
            self.state=GUIButtonState.NORMAL
        if rect is None:
            total_padding=self.margin+self.border_width+self.padding
            self.rect=(0,0,element.get_width()+2*total_padding,element.get_height()+2*total_padding)
        
        if element:
            element.style_name=style_name
            element.set_container(self)

    def set_disabled(self):
        self.state=GUIButtonState.DISABLED

    def set_enabled(self):
        self.state=GUIButtonState.NORMAL
       
    def handle_event(self,event,window_offset=(0,0)):
        if event.type == pygame.MOUSEMOTION:
            if point_in_rect( (event.pos[0]-window_offset[0],event.pos[1]-window_offset[1]),self.rect):
                #highlight it
                self.mouse_over()
                return False
            else:
                #unhighlight it
                self.mouse_not_over()
                return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if point_in_rect( (event.pos[0]-window_offset[0],event.pos[1]-window_offset[1]) ,self.rect):
                #click it
                self.mouse_button_down()
                return True
            else:
                return False
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_released()
            return False #doesn't consume the event
        #let's have buttons not have active elements
        #if self.element:
        #    return self.element.handle_event(event)
        return False
    
    def mouse_over(self):
        if self.state==GUIButtonState.DISABLED:
            return
        if self.state==GUIButtonState.NORMAL:
            self.state=GUIButtonState.HOVERED
            self.a_redraw_is_needed()

    def mouse_not_over(self):
        if self.state==GUIButtonState.DISABLED:
            return
        if self.state==GUIButtonState.HOVERED:
            self.state=GUIButtonState.NORMAL
            self.a_redraw_is_needed()
        elif self.state==GUIButtonState.CLICKED:
            self.state=GUIButtonState.NORMAL
            self.a_redraw_is_needed()
            

    def mouse_button_down(self):
        if self.state==GUIButtonState.DISABLED:
            return
        if self.state==GUIButtonState.HOVERED:
            self.state=GUIButtonState.CLICKED
            self.a_redraw_is_needed()
           

    def mouse_released(self):
        if self.state==GUIButtonState.DISABLED:
            return
        if self.state==GUIButtonState.CLICKED:
            self.state=GUIButtonState.HOVERED
            self.a_redraw_is_needed()
            self.register_click()

    def register_click(self):
        if self.on_click: #user supplied function
            self.on_click()
        print("Button clicked")
        ...

    def draw_screen(self,surf):
        if not super().draw_screen(surf):
            return False
        self.draw_border(surf)
        if self.state==GUIButtonState.NORMAL:
            pygame.draw.rect(surf,self.normal_bg,self.padded_rect)
        elif self.state==GUIButtonState.HOVERED:
            pygame.draw.rect(surf,self.hovered_bg,self.padded_rect)
        elif self.state==GUIButtonState.CLICKED:
            pygame.draw.rect(surf,self.clicked_bg,self.padded_rect)
        if self.element:
            clipped_content=clip_rect(self.content_rect,surf.get_rect())
            self.element.a_redraw_is_needed() #if I redrew the background, I need to redraw the element
            if clipped_content[2]>0 and clipped_content[3]>0:
                try:
                    self.element.draw_screen(surf.subsurface( clipped_content))
                except:
                    print("rect was {}".format(self.rect))
                    print("clipped content rect was {}".format(clipped_content))
                    print("surf was {}".format(surf.get_rect()))
                    raise(Exception("Error drawing button element"))
        return True

    def update_style(self,style={}):
        super().update_style(style)
        self.normal_bg=self.get_style_value("button_normal_bg",(200,200,200))
        self.hovered_bg=self.get_style_value("button_hovered_bg",(255,255,255))
        self.clicked_bg=self.get_style_value("button_clicked_bg",(255,0,0))
        self.disabled_bg=self.get_style_value("button_disabled_bg",(100,100,100))
        self.normal_border=self.get_style_value("button_normal_border",(255,255,255))
        self.hovered_border=self.get_style_value("button_hovered_border",(255,255,255))
        self.clicked_border=self.get_style_value("button_clicked_border",(255,255,255))
        self.disabled_border=self.get_style_value("button_disabled_border",(255,255,255))
        self.border_width=self.get_style_value("button_border_width",2)
        self.border_radius=self.get_style_value("button_border_radius",0)
        self.margin=self.get_style_value("button_margin",0) #area between the edge of the surface and the border
        self.padding=self.get_style_value("button_padding",0) #area between the border and the element
        if self.element:
            self.element.update_style(self.my_gui_style)

    def draw_border(self,surf):
        #clear the screen with bg color
        #pygame.draw.rect(surf,self.bg_color,(0,0,surf.get_width(),surf.get_height()))
        #draw border if necessary
        x0=self.rect[0]
        y0=self.rect[1]
        if self.border_width>0:
            if self.state==GUIButtonState.NORMAL:
                pygame.draw.rect(surf,self.normal_border,(x0+self.margin,y0+self.margin,self.rect[2]-2*self.margin,self.rect[3]-2*self.margin),self.border_width,self.border_radius)
            elif self.state==GUIButtonState.HOVERED:
                pygame.draw.rect(surf,self.hovered_border,(x0+self.margin,y0+self.margin,self.rect[2]-2*self.margin,self.rect[3]-2*self.margin),self.border_width,self.border_radius)
            elif self.state==GUIButtonState.CLICKED:
                pygame.draw.rect(surf,self.clicked_border,(x0+self.margin,y0+self.margin,self.rect[2]-2*self.margin,self.rect[3]-2*self.margin),self.border_width,self.border_radius)

    def resize(self,rect=None):
        super().resize(rect)
        rect=self.rect
        
        total_padding=self.margin+self.border_width+self.padding
        border_padding=self.margin+self.border_width
        self.padded_rect=(rect[0]+border_padding,rect[1]+border_padding,rect[2]-2*border_padding,rect[3]-2*border_padding)
        self.content_rect=(rect[0]+total_padding,rect[1]+total_padding,rect[2]-2*total_padding,rect[3]-2*total_padding)
        
        if self.element:
            self.element.resize((0,0,self.content_rect[2],self.content_rect[3]))

    def set_element(self,element):
        self.element=element
        if element is not None:
            element.set_container(self)

    def is_a_redraw_needed(self):
        if super().is_a_redraw_needed():
            return True
        if self.element and self.element.is_a_redraw_needed():
            return True
        return False

    def diagnose(self):
        print("GUIButton at {}".format(self.rect))

class GUITextButtonRow(GUIRowLayout):
    def __init__(self,rect,button_rect,button_text,my_on_click=None,style_name="default"):
        self.button_rect=button_rect
        self.buttons=[]
        self.my_on_click=my_on_click
        self.style_name=style_name
        super().__init__(self.buttons,rect,anchors=(GUIHAnchor.LEFT,GUIVAnchor.CENTER),style_name=style_name)
        for text in button_text:
            self.add_button(text)

    def add_button(self,text):
        #self.buttons.append(GUIButton(GUILabel(text),self.button_rect,on_click=lambda : self.on_click(text)))
        self.add_element(GUIButton(GUILabel(text,style_name=self.style_name),self.button_rect,on_click=lambda : self.on_click(text),style_name=self.style_name),1)


    def on_click(self,text):
        #print("Button clicked: "+text)
        if self.my_on_click:
            self.my_on_click(text)
        ...

class GUITextButtonCol(GUIColLayout):
    def __init__(self,rect,button_rect,button_text,my_on_click=None,style_name="default",anchors=(GUIHAnchor.CENTER,GUIVAnchor.TOP)):
        self.button_rect=button_rect
        self.buttons=[]
        self.my_on_click=my_on_click
        self.style_name=style_name

        super().__init__(self.buttons,rect,anchors=anchors,style_name=style_name)
        for text in button_text:
            self.add_button(text)

    def add_button(self,text):
        #print("adding button with rect {}".format(self.button_rect))
        #self.buttons.append(GUIButton(GUILabel(text),self.button_rect,on_click=lambda : self.on_click(text)))
        self.add_element(GUIButton(GUILabel(text,style_name=self.style_name),self.button_rect,on_click=lambda : self.on_click(text),style_name=self.style_name),1)

    def on_click(self,text):
        #print("Button clicked: "+text)
        if self.my_on_click:
            self.my_on_click(text)
        ...


class GUITextButtonPanel(GUIElement):
    def __init__(self,rect,my_style={}):
        self.buttons=[]
        self.n_columns=1
        self.inter_button_padding=0
        self.h_anchor=GUIHAnchor.CENTER
        self.v_anchor=GUIVAnchor.CENTER


        super().__init__(my_style)
        self.redraw_needed=True
        self.resize(rect)
        
        

    def setup_layout(self):
        #sort the buttons into columns
        elem_width=0
        elem_height=0
        for button in self.buttons:
            if button.get_width()>elem_width:
                elem_width=button.get_width()
            if button.get_height()>elem_height:
                elem_height=button.get_height()
        total_width=self.n_columns*elem_width+(self.n_columns+1)*self.inter_button_padding
        n_rows=len(self.buttons)//self.n_columns
        total_height=n_rows*elem_height+(n_rows+1)*elem_height
        xoffset=0
        yoffset=0
        if self.h_anchor==GUIHAnchor.CENTER:
            xoffset=(self.rect[2]-total_width)/2
        elif self.h_anchor==GUIHAnchor.RIGHT:
            xoffset=self.rect[2]-total_width
        if self.v_anchor==GUIVAnchor.CENTER:
            yoffset=(self.rect[3]-total_height)/2
        elif self.v_anchor==GUIVAnchor.BOTTOM:
            yoffset=self.rect[3]-total_height

        for i in range(len(self.buttons)):
            x0=(i%self.n_columns)*(elem_width+self.inter_button_padding)
            y0=(i//self.n_columns)*(elem_height+self.inter_button_padding)
            self.buttons[i].resize((xoffset+x0,yoffset+y0,elem_width,elem_height))

    def add_button(self,text):
        self.buttons.append(GUIButton(GUILabel(text),my_style=self.my_gui_style,on_click=lambda : self.on_click(text)))

    def resize(self,rect):
        self.rect=rect
        self.setup_layout()

    def needs_redraw(self):
        for button in self.buttons:
            if button.needs_redraw():
                return True
        return self.redraw_needed

    def draw_screen(self,surf):
        for button in self.buttons:
            button.draw_screen(surf)

    def handle_event(self,event,window_offset=(0,0)):
        for button in self.buttons:
            if button.handle_event(event,window_offset):
                return True
        return False

    def on_click(self,text):
        print("Button clicked: "+text)
        ...