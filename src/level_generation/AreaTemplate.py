from .RandomTable import RandomTable, parse_random_table_from_array
from ..level.MapRoom import MapRoom
from ..level.ObjectFactory import create_object_from_template
from ..level.MapCoord import MapCoord
import random
import yaml

class RoomTemplate:
    def __init__(self,template_name,**kwargs):
        self.template_name=template_name
        self.description=kwargs.get("description","")
        self.entities=None
        self.furnishings=None
        if "entities" in kwargs:
            self.entities=parse_random_table_from_array(kwargs["entities"])
        if "furnishings" in kwargs:
            self.furnishings=parse_random_table_from_array(kwargs["furnishings"])

    def apply_template(self,level,room):
        room.description=self.description
        if self.entities:
            self.add_table_objects(level,room,self.entities)
        if self.furnishings:
            self.add_table_objects(level,room,self.furnishings)

    def add_table_objects(self,level,room,table):
        for entry in table.realize():
            obj,quantity=entry
            possible_coords=room.get_coords_in_room_but_not_children()
            if len(possible_coords)==0:
                print("no possiblecoords")
                continue
            coords=random.sample(possible_coords,quantity)
            for coord in coords:
                print("adding ",obj," at ",coord[0],coord[1])
                thing=create_object_from_template(obj)
                level.add_object_to_cell(thing,MapCoord(coord[0],coord[1]))

class RoomTemplateStore:
    def __init__(self,fname):
        self.templates={}
        with open(fname) as f:
            data=yaml.safe_load(f)
            for entry,values in data.items():
                self.templates[entry]=RoomTemplate(entry,**values)

    def choose_random_template(self):
        return random.choice(list(self.templates.values()))
    
    def get_template(self,template_name):
        return self.templates[template_name]