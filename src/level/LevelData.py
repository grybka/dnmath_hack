import random
from collections import deque
from .MapCoord import MapCoord
from .GraphPaperMap import GraphPaperMap
from .ObjectStore import ObjectStore
from .GameObject import GameObject
from .Entity import Entity


class LevelData:
    def __init__(self):
        self.map=None
        self.memory_mask=None
        self.object_store=ObjectStore()
        self.room_store=None
        self.level_name=""
        self.player_respawn_point=MapCoord(0,0)
        self.tileset_name=""
        self.initiative={} #entity_id: initiative
        #self.initiative_order=[]  #list of (initiative,entity_id) tuples

    def add_object_to_cell(self,obj:GameObject,coord:MapCoord):
        obj.set_level(self)
        self.object_store.add_object(obj)
        self.map.add_object_to_cell(obj,coord)
        if isinstance(obj,Entity):
            self.add_to_entity_initiative(obj.id,obj.initiative)

    def delete_object(self,obj:GameObject):
        if obj.get_pos() is not None:
            self.map.remove_object_from_cell(obj,obj.get_pos())
        if isinstance(obj,Entity):
            self.initiative.pop(obj.id)
        self.object_store.delete_object(obj.id)

    #initiative handling - here or in gameengine
    def reset_initiative(self):
        entities=self.object_store.get_object_ids_of_class(Entity)
        self.initiative={}
        for entity_id in entities:
            self.initiative[entity_id]=0

    def get_next_entity_in_initiative(self):
        id=min(self.initiative,key=self.initiative.get)
        return id
        
    def add_to_entity_initiative(self,entity_id,initiative):
        initiative+=self.initiative.get(entity_id,0)
        self.initiative[entity_id]=initiative
        


class LevelStore:
    def __init__(self):
        self.levels={} #organized by name