import random
import uuid
from ..level.MapCoord import MapCoord
from ..level.GraphPaperMap import GraphPaperMap, CellType, WallType
from .WallObject import DoorObject

class MapRoomExit:
    def __init__(self,coord,direction,has_door=False):
        self.coord=coord
        self.direction=direction #by convention points out
        self.has_door=has_door

class MapRoom:
    def __init__(self,rect,id=None,parent=None):
        self.description=""
        self.rect=rect #[x,y,width,height] with x,y being the upper left
        self.exits=[]
        if id is None:
            self.id=uuid.uuid4()
        else:
            self.id=id
        self.parent=parent
        self.children=[]

    def choose_edge(self,padding=0):
        side=random.randint(0,3)
        if side==0:
            return [random.randint(self.rect[0]+padding,self.rect[0]+self.rect[2]-1-padding),self.rect[1],0]
        if side==1:
            return [self.rect[0]+self.rect[2]-1,random.randint(self.rect[1]+padding,self.rect[1]+self.rect[3]-1-padding),1]
        if side==2:
            return [random.randint(self.rect[0]+padding,self.rect[0]+self.rect[2]-1-padding),self.rect[1]+self.rect[3]-1,2]
        if side==3:
            return [self.rect[0],random.randint(self.rect[1]+padding,self.rect[1]+self.rect[3]-1-padding),3]

    def create_exits(self,n_exits,width=0,has_doors=False):
        for i in range(n_exits):
            edge_and_dir=self.choose_edge(width)
            self.exits.append(MapRoomExit(edge_and_dir[0:2],edge_and_dir[2],has_door=has_doors))

    def create_double_exit(self):
        self.exits.append( MapRoomExit( [self.rect[0]+self.rect[2]//2,self.rect[1]],0 ))
        self.exits.append( MapRoomExit( [self.rect[0]+self.rect[2]//2+1,self.rect[1]],0))

    def get_relative_coord(self,coord):
        return MapCoord(self.rect[0],self.rect[1])+coord

    def get_center(self):
        return [self.rect[0]+self.rect[2]//2,self.rect[1]+self.rect[3]//2]
            

    def dig_self_on_map(self,map,cell_type=CellType.INDOOR_CLEAN_FLOOR):
        #remove the stone or floor or whatever
        map.fill(self.rect,cell_type)
        map.set_room(self.id,self.rect)

    def clear_of_objects(self,level):
        map=level.map
        for x in range(self.rect[0],self.rect[0]+self.rect[2]):
            for y in range(self.rect[1],self.rect[1]+self.rect[3]):
                objects=map.get_objects_in_cell(MapCoord(x,y)).copy()
                for obj in objects:
                    print("removing object {}".format(obj.reference_noun(specific=False)))
                    level.delete_object(obj)

    def build_walls(self,map):
        #build the walls, plaster over exits 
        for x in range(self.rect[0],self.rect[0]+self.rect[2]):
            #North Wall            
            map.get_wall(MapCoord(x,self.rect[1]),0).wall_type=WallType.WALL
            if map.get_opposite_wall(MapCoord(x,self.rect[1]),0) is not None:
                map.get_opposite_wall(MapCoord(x,self.rect[1]),0).wall_type=WallType.WALL
            #South Wall
            map.get_wall(MapCoord(x,self.rect[1]+self.rect[3]-1),2).wall_type=WallType.WALL
            if map.get_opposite_wall(MapCoord(x,self.rect[1]+self.rect[3]-1),2) is not None:
                map.get_opposite_wall(MapCoord(x,self.rect[1]+self.rect[3]-1),2).wall_type=WallType.WALL
        for y in range(self.rect[1],self.rect[1]+self.rect[3]):
            #West Wall
            map.get_wall(MapCoord(self.rect[0],y),3).wall_type=WallType.WALL
            if map.get_opposite_wall(MapCoord(self.rect[0],y),3) is not None:
                map.get_opposite_wall(MapCoord(self.rect[0],y),3).wall_type=WallType.WALL
            #East Wall
            map.get_wall(MapCoord(self.rect[0]+self.rect[2]-1,y),1).wall_type=WallType.WALL
            if map.get_opposite_wall(MapCoord(self.rect[0]+self.rect[2]-1,y),1) is not None:
                map.get_opposite_wall(MapCoord(self.rect[0]+self.rect[2]-1,y),1).wall_type=WallType.WALL
        for exit in self.exits:
            if exit.has_door:
                door_obj=DoorObject()
                map.add_object_to_wall(door_obj,MapCoord(exit.coord[0],exit.coord[1]),exit.direction)
                door_obj.update_wall()
            else:
                map.set_wall_type(MapCoord(exit.coord[0],exit.coord[1]),exit.direction,WallType.NONE)
            #map.get_wall(MapCoord(exit.coord[0],exit.coord[1]),exit.direction).wall_type=WallType.NONE
            #if map.get_opposite_wall(MapCoord(exit.coord[0],exit.coord[1]),exit.direction) is not None:
            #    map.get_opposite_wall(MapCoord(exit.coord[0],exit.coord[1]),exit.direction).wall_type=WallType.NONE


    def set_lighting(self,map,light_level):
        for x in range(self.rect[0],self.rect[0]+self.rect[2]):
            for y in range(self.rect[1],self.rect[1]+self.rect[3]):
                map.get_cell(MapCoord(x,y)).ambient_light_level=light_level

    def coord_in_room(self,coord):
        return coord[0]>=self.rect[0] and coord[0]<self.rect[0]+self.rect[2] and coord[1]>=self.rect[1] and coord[1]<self.rect[1]+self.rect[3]

    def coord_in_children(self,coord):
        for child in self.children:
            if child.coord_in_room(coord):
                return True
        return False

    def get_coords_in_room_but_not_children(self):
        coords=[]
        for x in range(self.rect[0],self.rect[0]+self.rect[2]):
            for y in range(self.rect[1],self.rect[1]+self.rect[3]):
                if not self.coord_in_children([x,y]):
                    coords.append([x,y])
        return coords
    
    def get_random_coord_in_room(self):
        coords=self.get_coords_in_room_but_not_children()
        if len(coords)==0:
            return None
        return random.choice(coords)


class MapRoomStore:
    def __init__(self):
        self.rooms={}
        self.room_alias={}

    def add_room(self,room):
        self.rooms[room.id]=room

    def add_room_alias(self,room_id,alias):
        if room_id not in self.rooms:
            raise Exception("Room {} not found to alias".format(room_id))
        self.room_alias[alias]=room_id

    def get_room_by_id(self,id):
        if id in self.rooms:
            return self.rooms[id]
        if id in self.room_alias:
            return self.rooms[self.room_alias[id]]
        raise Exception("Room {} not found".format(id))
        return None

#a structure outside
class MRHouse(MapRoom):
    def __init__(self,rect):
        super().__init__(rect)

#This is used to flag an are that is an exit
class MRExit(MapRoom):
    def __init__(self,rect,to_level,level_spawn_point):
        super().__init__(rect)

    def dig_self_on_map(self,map):
        #remove the stone or floor or whatever
        map.fill(self.rect,CellType.EXIT)
        map.set_room(self.id,self.rect)
       
