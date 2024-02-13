#base class for level generation, mostly helper functions
from ..level.LevelData import LevelData, LevelPortal
from ..level.MapCoord import MapCoord
from ..level.GraphPaperMap import GraphPaperMap, CellType
from ..level.ObjectFactory import create_object_from_template
from .RandomTable import parse_table_entry
from .AreaTemplate import RoomTemplate, RoomTemplateStore

import random

class LevelGenerator:
    def __init__(self,**kwargs):
        self.xsize=kwargs.get("xsize",20)
        self.ysize=kwargs.get("ysize",20)
        self.level=LevelData()
        self.level.map=GraphPaperMap(self.xsize,self.ysize)
        portals=kwargs.get("portals",{})
        for key in portals:
            self.level.portals[key]=LevelPortal(**portals[key])
#            self.level.portals[key]=LevelPortal(MapCoord(portals[key]["coord"]),portals[key]["target_level"],portals[key]["target_entry_point"])
        self.area_templates=RoomTemplateStore("data/levels/room_tables.yaml")
        self.must_have_rooms=kwargs.get("must_have_rooms",[])

    def select_area_template(self):
        return self.area_templates.choose_random_template()
        #if len(self.area_templates)==0:
        #    return None
        #weights=[x["weight"] for x in self.area_templates]
        #return random.choices(self.area_templates,weights,k=1)[0]

    def choose_random_square_of_type(self,cell_types):
        if not isinstance(cell_types,list):
            cell_types=[cell_types]
        map=self.level.map
        valid_coords=[]
        for i in range(map.width):
            for j in range(map.height):
                if map.get_cell_type(MapCoord(i,j)) in cell_types:
                    valid_coords.append(MapCoord(i,j))
        if len(valid_coords)==0:
            print("Failed to find a square of type {}".format(cell_type))
            return None                    
        return random.choice(valid_coords)

    def add_furnishings(self,level):
        if "areas" not in self.info:
            return
        #TODO nonrandom furnishings
        #TODO random furnishings
        print("adding random furnishings")
        for area,areainfo in self.info["areas"].items():
            print("on area ",area)
            room=level.room_store.get_room_by_id(area)
            if "furnishings_random" not in areainfo:
                print("no random furnishings")
                continue
            for obj in areainfo["furnishings_random"]:
                if "table" in obj:
                    to_roll=parse_table_entry(obj["table"])
                    vals=to_roll.realize()
                    for val in vals:
                        quantity=val[1]
                        objtype=val[0]
                        possible_coords=room.get_coords_in_room_but_not_children()
                        if len(possible_coords)==0:
                            print("no possiblecoords")
                            continue
                        coords=random.sample(possible_coords,quantity)
                        for coord in coords:
                            print("adding ",objtype," at ",coord[0],coord[1])
                            thing=create_object_from_template(objtype)
                            level.add_object_to_cell(thing,MapCoord(coord[0],coord[1]))
                else:
                    quantity=obj["quantity"]
                    possible_coords=room.get_coords_in_room_but_not_children()
                    if len(possible_coords)==0:
                        print("no possiblecoords")
                        continue
                    coords=random.sample(possible_coords,quantity)
                    for coord in coords:
                        print("adding ",obj["type"]," at ",coord[0],coord[1])
                        thing=create_object_from_template(obj["type"])
                    level.add_object_to_cell(thing,MapCoord(coord[0],coord[1]))

    def add_portals(self,level):
        for key in level.portals:
            portal=level.portals[key]
            if portal.coord is None:
                if portal.room is None:
                    print("Warning, just putting the portal in a random square")
                    #choose a random square of the right type
                    portal.coord=self.choose_random_square_of_type([CellType.INDOOR_FLOOR,CellType.OUTDOOR_GRASS,CellType.INDOOR_CLEAN_FLOOR])
                else:
                    room=level.room_store.get_room_by_id(portal.room)
                    portal.coord=MapCoord(room.get_random_coord_in_room())
                    #portal.coord=room.get_center()
            if portal.type!="entrance_only":
                level.map.set_cell_type(portal.coord,CellType.EXIT)
            if portal.type=="stairs_up":
                level.add_object_to_cell(create_object_from_template("stairs_up"),portal.coord)
            if portal.type=="stairs_down":
                level.add_object_to_cell(create_object_from_template("stairs_down"),portal.coord)

    def apply_template_to_room(self,template,room,level):
        if template is None:
            return
        for obj in template["furnishings_random"]:
            if "table" in obj:
                to_roll=parse_table_entry(obj["table"])
                vals=to_roll.realize()
                for val in vals:
                    quantity=val[1]
                    objtype=val[0]
                    possible_coords=room.get_coords_in_room_but_not_children()
                    if len(possible_coords)==0:
                        print("no possiblecoords")
                        continue
                    coords=random.sample(possible_coords,quantity)
                    for coord in coords:
                        print("adding ",objtype," at ",coord[0],coord[1])
                        thing=create_object_from_template(objtype)
                        level.add_object_to_cell(thing,MapCoord(coord[0],coord[1]))
