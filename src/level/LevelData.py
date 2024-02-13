import random
from collections import deque
from .MapCoord import MapCoord
from .GraphPaperMap import GraphPaperMap
from .MapRoom import MapRoomStore
from .ObjectStore import ObjectStore
from .GameObject import GameObject
from .Entity import Entity

class LevelPortal:
#    def __init__(self,coord:MapCoord,target_level:str,target_entry_point:str):
    def __init__(self,**kwargs):
        if "coord" in kwargs:
            self.coord=MapCoord(kwargs["coord"][0],kwargs["coord"][1])
        else:
            self.coord=None
        self.target_level=kwargs["target_level"]
        self.target_entry_point=kwargs["target_entry_point"]
        self.type=kwargs["type"]
        self.room=kwargs.get("room",None)
#        self.coord=coord
#        self.target_level=target_level
#        self.target_entry_point=target_entry_point
#        self.type="portal"

class LevelData:
    def __init__(self):
        self.map=None
        self.memory_mask=None
        self.object_store=ObjectStore()
        self.room_store=MapRoomStore()
        self.level_name=""
        self.player_respawn_point=MapCoord(0,0)
        self.tileset_name=""
        self.initiative={} #entity_id: initiative
        self.portals={}
        #self.entry_points={}
        #self.exit_points={} #MapCoord: (level_name,entry_point)
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

    #Rooms
        
    def get_room_at(self,coord:MapCoord):
        return self.room_store.rooms[self.map.get_cell(coord).room_id]
    
    def get_entry_point_location(self,entry_point):
        return self.portals[entry_point].coord
    
    def get_exit_portal(self,exit_pos):
        for key in self.portals:
            if self.portals[key].coord==exit_pos:
                return self.portals[key]
        return None

    def get_exit_destination(self,exit_pos):
        for key in self.portals:
            if self.portals[key].coord==exit_pos:
                return self.portals[key].target_level,self.portals[key].target_entry_point
        return None,None
        


class LevelStore:
    def __init__(self):
        self.levels={} #organized by name