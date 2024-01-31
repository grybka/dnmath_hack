
class GUIActivity:
    def __init__(self,mainwindow,engine):
        self.mainwindow=mainwindow
        self.engine=engine

    def update(self,clock_time):
        ...

    def handle_event(self,event):
        return False #return true if event is handled and should not be passed to other elements

#everything waits until the map animation is over
class GUIWaitForMapAnimation(GUIActivity):
    def __init__(self,mainwindow,engine,animation):
        super().__init__(mainwindow,engine)
        self.animation=animation

    def update(self,clock_time):
        if self.animation.is_done():
            return True
        return False

class GUISelectObject(GUIActivity):
    def __init__(self,mainwindow,engine):
        super().__init__(mainwindow,engine)
        self.selected_object=None
        self.mainwindow.mapview.deselect_all()

    def update(self,clock_time):
        if self.mainwindow.mapview.get_selected_cell is not None:
            objects=self.engine.level.map.get_objects_in_cell(self.mainwindow.mapview.get_selected_cell)
            if len(objects)==0:
                return False
            self.selected_object=objects[0]
            return True
        return False