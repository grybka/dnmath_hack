import pygame

from ..gui_core.GUIElement import GUIElement, GUIHAnchor,GUIVAnchor
from ..gui_core.GUITextBox import GUITextBox, GUILabel
from ..gui_core.GUIPane import GUIPane


class GUIInfoPopup(GUIPane):
    def __init__(self,engine,mainwindow,message):
        self.engine=engine
        self.mainwindow=mainwindow
        self.message=message
        self.text_box=GUITextBox()
        self.text_box.set_text(message)
        height=self.mainwindow.get_height()//4
        width=self.mainwindow.get_width()//2
        super().__init__(self.text_box,(0,0,width,height),anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])

    def handle_event(self,event,window_offset=None):
        if event.type==pygame.MOUSEBUTTONDOWN:
            self.mainwindow.remove_popup_window(self)
            return True
        return False