import pygame
from gui_core.GUIElement import GUIElement,GUIHAnchor,GUIVAnchor
from gui_core.GUIManager import GUIManager
from gui_core.GUIPane import *
from gui_core.GUITextBox import GUITextBox,GUILabel
from gui_core.GUIButton import GUIButton, GUITextButtonPanel
pygame.init()
pygame.font.init()

displayinfo=pygame.display.Info()
max_x=2*1024
max_y=2*768
if displayinfo.current_w*0.9<max_x:
    max_x=int(displayinfo.current_w*0.9)
if displayinfo.current_h*0.8<max_y:
    max_y=int(displayinfo.current_h*0.9)
resolution=(max_x,max_y)

screen=pygame.display.set_mode(resolution)
clock=pygame.time.Clock()

def the_loop(gui_manager):
    running=True
    while running:
        clock.tick(60)
        gui_manager.draw_screen(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                full.resize((0,0,screen.get_width(),screen.get_height()) )
            if event.type == pygame.QUIT:
                running=False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running=False
            gui_manager.handle_event(event)
        gui_manager.update(clock.get_time())


def test_0():
    gui_manager=GUIManager(resolution)
    gui_manager.load_style_file("../data/gui_style.yaml")

    label1=GUILabel("Label Test CENTER")
    label2=GUILabel("Label Test LL",my_style={"label_text_color":(0,255,0)})
    label3=GUILabel("Label Test RESIZE")
    print("label 1 rect {}".format(label1.rect))
    pane1=GUIPane(label1,(0,0,200,200),anchors=(GUIHAnchor.CENTER,GUIVAnchor.CENTER),my_style={"bg_color":(255,0,0)})
    pane2=GUIPane(label2,(200,0,200,200),anchors=(GUIHAnchor.LEFT,GUIVAnchor.BOTTOM))
    pane3=GUIPane(label3,(400,0,200,200),anchors=(GUIHAnchor.RESIZE,GUIVAnchor.RESIZE))

    gui_manager.add_element(pane1)
    gui_manager.add_element(pane2)
    gui_manager.add_element(pane3)
    the_loop(gui_manager)

def test_0p1():
    gui_manager=GUIManager(resolution)
    gui_manager.load_style_file("../data/gui_style.yaml")

    label1=GUILabel("Label Test CENTER",my_style={"label_text_color":(0,255,0)})
    label2=GUILabel("Label Test LL",my_style={"label_text_color":(0,255,0)})
    label3=GUILabel("Label Test RESIZE",my_style={"label_text_color":(0,255,0)})

    rows=GUIRowLayout([label1,label2,label3],(0,0,600,200),anchors=(GUIHAnchor.CENTER,GUIVAnchor.CENTER))
    gui_manager.add_element(rows)
    the_loop(gui_manager)

    




#Test Pane, Label, Button, GUIScaledColLayout, GUIScaledRowLayout
def test_1():
    gui_manager=GUIManager(resolution)
    gui_manager.load_style_file("../data/gui_style.yaml")

    label1=GUILabel("Label Test")
    label2=GUILabel("Hello World")

    button=GUIButton(GUILabel("Button Test"),(0,0,100,20))
    button2=GUIButton(GUILabel("Disabled Button Test"),(0,0,100,20),is_disabled=True)
    #ulpane=GUIPane(GUIWindowStack([label1,button2]),(0,0,0,0))
    ulpane=GUIPane(GUIRowLayout([label1,button2],(0,0,0,0)),(0,0,0,0))
    urpane=GUIPane(button,(0,0,0,0))

        
    llpane=GUIPane(label1,(0,0,0,0))
    textbox=GUITextBox(anchors= (GUIHAnchor.LEFT,GUIVAnchor.TOP) )
    textbox.print("First line")
    textbox.print("Second line")
    lrpane=GUIPane(textbox,(0,0,0,0))

    left_side=GUIColLayout([ulpane,llpane],element_proportions=[2,1],rect=(0,0,0,0))
    right_side=GUIColLayout([urpane,lrpane],element_proportions=[1,1],rect=(0,0,0,0))
    full=GUIRowLayout([left_side,right_side],element_proportions=[2,1],rect=(0,0,screen.get_width(),screen.get_height()))

    gui_manager.add_element(full)
        
    the_loop(gui_manager)

def test_2():
    gui_manager=GUIManager(resolution)
    gui_manager.load_style_file("../data/gui_style.yaml")

    label1=GUILabel("Label Test")
    llpane=GUIPane(label1,(0,0,0,0))

    button_panel=GUITextButtonPanel((0,0,0,0))
    button_panel.n_columns=2
    button_panel.add_button("Button 1")
    button_panel.add_button("Button 2")
    button_panel.add_button("Button 3")
    button_panel.add_button("Button 4")
    button_panel.add_button("Button 5")
    print("button style ",button_panel.get_default_gui_style())
    print("button margin ",button_panel.buttons[0].get_style_value("button_margin"))
    ulpane=GUIPane(button_panel,(0,0,0,0))
    
    full=GUIScaledColLayout([ulpane,llpane],[2,1],(0,0,screen.get_width(),screen.get_height()))
    gui_manager.add_element(full)
        
    the_loop(gui_manager)


def test_3():
    gui_manager=GUIManager(resolution)
    gui_manager.load_style_file("../data/gui_style.yaml")

    label=[]
    for i in range(12):
        label.append(GUILabel("Label {}".format(i),style_name="default_label"))
    #row1=GUIPane(label[0],(0,0,500,100))
    row1=GUIPane(GUIRowLayout( [label[0],label[1],label[2]],(0,0,500,100),anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP)) ,(0,0,500,100))
    row2=GUIPane(GUIRowLayout( [label[3],label[4],label[5]],(0,0,500,100),anchors=(GUIHAnchor.CENTER,GUIVAnchor.CENTER)) ,(0,100,500,100))
    row3=GUIPane(GUIRowLayout( [label[6],label[7],label[8]],(0,0,500,100),anchors=(GUIHAnchor.RIGHT,GUIVAnchor.BOTTOM)) ,(0,200,500,100))
    row4=GUIPane(GUIRowLayout( [label[9],label[10],label[11]],(0,0,500,100),anchors=(GUIHAnchor.RESIZE,GUIVAnchor.RESIZE),element_proportions=[1,1,2]) ,(0,300,500,100))


    gui_manager.add_element(row1)
    gui_manager.add_element(row2)
    gui_manager.add_element(row3)
    gui_manager.add_element(row4)

    the_loop(gui_manager)
    

def test_4():
    gui_manager=GUIManager(resolution)
    gui_manager.load_style_file("../data/gui_style.yaml")

    label=[]
    for i in range(12):
        label.append(GUILabel("Label {}".format(i),style_name="default_label"))
    #row1=GUIPane(label[0],(0,0,500,100))
    row1=GUIPane(GUIColLayout( [label[0],label[1],label[2]],(0,0,200,600),anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP)) ,(0,0,200,600))
    row2=GUIPane(GUIColLayout( [label[3],label[4],label[5]],(0,0,200,600),anchors=(GUIHAnchor.CENTER,GUIVAnchor.CENTER)) ,(200,0,200,600))
    row3=GUIPane(GUIColLayout( [label[6],label[7],label[8]],(0,0,200,600),anchors=(GUIHAnchor.RIGHT,GUIVAnchor.BOTTOM)) ,(400,0,200,600))
    row4=GUIPane(GUIColLayout( [label[9],label[10],label[11]],(0,0,200,600),anchors=(GUIHAnchor.RESIZE,GUIVAnchor.RESIZE),element_proportions=[1,1,2]) ,(600,0,200,600))

    gui_manager.add_element(row1)
    gui_manager.add_element(row2)
    gui_manager.add_element(row3)
    gui_manager.add_element(row4)

    the_loop(gui_manager)

def test_5():
    gui_manager=GUIManager(resolution)
    gui_manager.load_style_file("../data/gui_style.yaml")

    label=[]
    for i in range(12):
        label.append(GUILabel("Label {}".format(i),style_name="default_label"))
    #row1=GUIPane(label[0],(0,0,500,100))
    row1=GUIPane(GUIColLayout( [label[0],label[1],label[2]],(0,0,100,400),anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP)) ,(0,0,100,100))
    row2=GUIPane(GUIColLayout( [label[3],label[4],label[5]],(0,0,100,400),anchors=(GUIHAnchor.CENTER,GUIVAnchor.CENTER)) ,(0,0,100,100))
    row3=GUIPane(GUIColLayout( [label[6],label[7],label[8]],(0,0,100,400),anchors=(GUIHAnchor.RIGHT,GUIVAnchor.BOTTOM)) ,(0,0,100,100))
    row4=GUIPane(GUIColLayout( [label[9],label[10],label[11]],(0,0,100,400),anchors=(GUIHAnchor.RESIZE,GUIVAnchor.RESIZE),element_proportions=[1,1,2]) ,(0,0,100,100))

    button1=GUIButton(GUILabel("button 1"),[0,0,200,50])
    labelmid=GUILabel("inbetween",style_name="default_label")
    button2=GUIButton(GUILabel("button 2"),[0,0,200,50])
    row5=GUIPane(GUIColLayout( [button1,labelmid,button2],(0,0,100,400),anchors=(GUIHAnchor.LEFT,GUIVAnchor.TOP)),(0,0,100,400))

    full=GUIRowLayout([row4,row2,row3,row1,row5],(0,0,500,400),element_proportions=[1,1,1,2,8],anchors=[GUIHAnchor.RESIZE,GUIVAnchor.RESIZE])

    gui_manager.add_element(full)
   
    the_loop(gui_manager)






test_5()





#textmenu=GUIWordMenu()
#textmenu.add_option("Option 1",(255,0,0))
#textmenu.add_option("Option 2",(0,255,0))
#textmenu.add_option("Option 3",(0,0,255))
#textmenu.add_option("Option 4",(255,255,0))
#textmenu.add_option("Option 5",(255,0,255))
#textmenu.add_option("Option 6",(0,255,255))
#textmenu.n_cols=2




#left_side=GUIScaledColLayout([ulpane,llpane],[2,1],(0,0,0,0))
#right_side=GUIScaledColLayout([urpane,lrpane],[1,1],(0,0,0,0))
#full=GUIScaledRowLayout([left_side,right_side],[2,1],(0,0,screen.get_width(),screen.get_height()))
#gui_manager=GUIManager(resolution)
#gui_manager.load_style_file("data/gui_style.yaml")
#gui_manager.add_element(full)

