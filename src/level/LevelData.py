from .MapCoord import MapCoord
from .GraphPaperMap import GraphPaperMap
from .ObjectStore import ObjectStore
from .GameObject import GameObject

class LevelData:
    def __init__(self):
        self.map=None
        self.object_store=ObjectStore()
        self.room_store=None
        self.level_name=""
        self.player_respawn_point=MapCoord(0,0)
        self.tileset_name=""

    def add_object_to_cell(self,obj:GameObject,coord:MapCoord):
        obj.set_level(self)
        self.object_store.add_object(obj)
        self.map.add_object_to_cell(obj,coord)

    def delete_object(self,obj:GameObject):
        if obj.get_pos() is not None:
            self.map.remove_object_from_cell(obj,obj.get_pos())
        self.object_store.delete_object(obj.id)
                                         


class LevelStore:
    def __init__(self):
        self.levels={} #organized by name