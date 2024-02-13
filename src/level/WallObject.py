from .GameObject import GameObject
from ..level.GraphPaperMap import CellType, WallType


class DoorObject(GameObject):
    def __init__(self,**kwparams):
        super().__init__(**kwparams)
        object=kwparams.get("object",{})
        self.is_open=object.get("is_open",False)
        self.noun=object.get("reference","door")

        self.wall=None
        #self.is_locked=object.get("is_locked",False)
       
    def set_wall(self,wall):
        self.wall=wall

    def open(self):
        self.is_open=True
        self.update_wall()

    def close(self):
        self.is_open=False
        self.update_wall()

    def update_wall(self):
        #print("updating wall {}".format(self.wall))
        if self.wall is None:
            return
        if self.is_open:
            self.wall.wall_type=WallType.DOOR_OPEN
        else:
            self.wall.wall_type=WallType.DOOR_CLOSED
        if self.wall.opposite_wall is not None:
            self.wall.opposite_wall.wall_type=self.wall.wall_type