from enum import Enum
import uuid
import copy
import random
from .MapCoord import MapCoord,Direction,opposite_dir,left_of,right_of

class CellType(Enum):
    OUTDOOR_GRASS = 0
    INDOOR_FLOOR = 1
    INDOOR_CLEAN_FLOOR = 2
    STONE =3
    IMPASSIBLE = 4
    WATER = 5
    EXIT = 6
#    DIRT = 0 #floor
#    STONE = 1 #solid
#    IMPASSIBLE = 2
#    WATER = 3

class WallType(Enum):
    NONE = 0
    WALL = 1
    DOOR_CLOSED = 2
    DOOR_OPEN = 3

class CellVisibility(Enum):
    VISIBLE = 0
    HIDDEN = 1
    REMEMBERED = 2

def string_to_celltype(s):
    return CellType[s.upper()]

#some utility functions
def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def clip(val,min,max):
    if val<min:
        return min
    if val>max:
        return max
    return val

def on_segment(p,q,r):
    if q[0]<=max(p[0],r[0]) and q[0]>=min(p[0],r[0]) and q[1]<=max(p[1],r[1]) and q[1]>=min(p[1],r[1]):
        return True
    return False

# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


    
class GPWall:
    def __init__(self,wall_type):
        self.wall_type=wall_type
        self.random_number=random.randint(0,2047)
        self.opposite_wall=None #the wall coming from the other side
        self.contents=[] #what objects are in the wall, like doors
    def __str__(self):
        return "GPWall("+str(self.wall_type)+")"
    def __repr__(self):
        return self.__str__()

class GPCell:
    def __init__(self,cell_type):
        self.cell_type=cell_type
        self.room_id=None #what room is it in
        self.objects=[] #what objects are in the cell
        self.random_number=random.randint(0,2047)
        self.walls=[GPWall(WallType.NONE) for i in range(4)] #N,E,S,W
        self.light_level=0 # 0-255
        self.ambient_light_level=0
        
    def __str__(self):
        return "GPCell("+str(self.cell_type)+")"
    def __repr__(self):
        return self.__str__()
    
class MapMask:
    def __init__(self,width,height):
        self.width=width
        self.height=height
        self.cells=[]
        for x in range(width):
            row=[]
            for y in range(height):
                row.append(CellVisibility.HIDDEN)
                #row.append(CellVisibility.VISIBLE)
                #row.append(CellVisibility.REMEMBERED)


            self.cells.append(row)

    def set_visible(self,x,y):
        if x>=0 and x<self.width and y>=0 and y<self.height:
            self.cells[x][y]=CellVisibility.VISIBLE

    def set_remembered(self,x,y):
        if x>=0 and x<self.width and y>=0 and y<self.height:
            self.cells[x][y]=CellVisibility.REMEMBERED

    def visible_to_remembered(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.cells[x][y]==CellVisibility.VISIBLE:
                    self.cells[x][y]=CellVisibility.REMEMBERED

class GraphPaperMap:
    def __init__(self,width,height):
        self.width=width
        self.height=height
        self.cells=[]
        for x in range(width):
            row=[]
            for y in range(height):
                row.append(GPCell(CellType(0)))
            self.cells.append(row)
        #connect up the walls
        for x in range(width):
            for y in range(height):
                for direction in range(4):
                    self.cells[x][y].walls[direction].opposite_wall=self.get_opposite_wall(MapCoord(x,y),Direction(direction))
        self.ambient_light=255 #the default light level without a light source
        print("intersect test {}".format(intersect(MapCoord(3.5,3.5),MapCoord(3.5,2.5),MapCoord(3,4),MapCoord(4,4))))

    def add_object_to_cell(self,object,coord:MapCoord):
        object.set_pos(coord)
        self.cells[coord.x][coord.y].objects.append(object)

    def add_object_to_wall(self,object,coord:MapCoord,direction:Direction):
        if isinstance(direction,int):
            direction=Direction(direction)
        self.cells[coord.x][coord.y].walls[direction.value].contents.append(object)
        if self.get_opposite_wall(coord,direction) is not None:
            self.get_opposite_wall(coord,direction).contents.append(object)
        #TODO, how does the wall think about this?
        object.set_wall(self.cells[coord.x][coord.y].walls[direction.value])

    def remove_object_from_cell(self,object,coord):
        self.cells[coord.x][coord.y].objects.remove(object)
        object.set_pos(None)

    def fill(self,rect,cell_type):
        if rect is None:
            rect=[0,0,self.width,self.height]
        for x in range(rect[0],rect[0]+rect[2]):
            for y in range(rect[1],rect[1]+rect[3]):
                self.cells[x][y].cell_type=cell_type

    def set_room(self,room_id,rect=None):
        if rect is None:
            rect=[0,0,self.width,self.height]
        for x in range(rect[0],rect[0]+rect[2]):
            for y in range(rect[1],rect[1]+rect[3]):
                self.cells[x][y].room_id=room_id

    def blit(self,coord,other_map):
        #copy the other map onto this map
        for x in range(other_map.width):
            for y in range(other_map.height):
                self.cells[coord.x+x][coord.y+y]=copy.deepcopy(other_map.cells[x][y])

    def is_on_map(self,coord):
        return coord.x>=0 and coord.x<self.width and coord.y>=0 and coord.y<self.height

    def is_passable(self,coord,direction,passable_cell_types=[CellType.OUTDOOR_GRASS,CellType.INDOOR_FLOOR,CellType.INDOOR_CLEAN_FLOOR],passable_wall_types=[WallType.NONE,WallType.DOOR_OPEN]):
        new_coord=coord+MapCoord.direction_to_vector(direction)
        #you cannot move off map
        if not self.is_on_map(new_coord):
            print("trying to move off map")
            return False
        #you cannot move through walls
        if self.cells[coord.x][coord.y].walls[direction.value].wall_type not in passable_wall_types:
            print("trying to move through wall")
            return False
        #you cannot move through impassible cells
        if self.cells[new_coord.x][new_coord.y].cell_type in passable_cell_types:
            return True
        print("cell type is {}".format(self.cells[new_coord.x][new_coord.y].cell_type))

        return False
    
    def get_cell(self,coord:MapCoord):
        if not self.is_on_map(coord):
            return None
        return self.cells[coord.x][coord.y]
    
    def get_cell_type(self,coord:MapCoord):
        return self.cells[coord.x][coord.y].cell_type

    def set_cell_type(self,coord:MapCoord,cell_type):
        self.cells[coord.x][coord.y].cell_type=cell_type
    
    def get_wall_type(self,coord:MapCoord,direction):
        return self.cells[coord.x][coord.y].walls[direction.value].wall_type
    
    def get_wall(self,coord:MapCoord,direction:Direction):
        if isinstance(direction,int):
            direction=Direction(direction)
        if not self.is_on_map(coord):
            return None
        return self.cells[coord.x][coord.y].walls[direction.value]
    
    def get_opposite_wall(self,coord:MapCoord,direction:Direction):
        #Returns the wall corresponding the other side of the wall you're pointing at
        if not self.is_on_map(coord):
            return None
        other_cell=coord+MapCoord.direction_to_vector(direction)
        if not self.is_on_map(other_cell):
            return None
        try:
            return self.cells[other_cell.x][other_cell.y].walls[opposite_dir(direction).value]
        except:
            print("coord: "+str(coord))
            print("other_cell: "+str(other_cell))
            print("direction: "+str(direction))
            print("opposite_dir: "+str(opposite_dir(direction)))
            print("other cell {}".format(self.cells[other_cell.x][other_cell.y]))
            print("other cell walls {}".format(self.cells[other_cell.x][other_cell.y].walls))

    def set_wall_type(self,coord:MapCoord,direction:Direction,wall_type:WallType):
        if isinstance(direction,int):
            direction=Direction(direction)
        self.cells[coord.x][coord.y].walls[direction.value].wall_type=wall_type
        opposite_wall=self.get_opposite_wall(coord,direction)
        if opposite_wall is not None:
            opposite_wall.wall_type=wall_type
    
    def get_objects_in_cell(self,coord:MapCoord):
        ret=self.cells[coord.x][coord.y].objects
        for wall in self.cells[coord.x][coord.y].walls:
            ret+=wall.contents
        return ret
    
    def get_objects_within_radius(self,pos,radius):
        objects=[]
        for x in range(-radius,radius+1):
            for y in range(-radius,radius+1):
                new_pos=pos+MapCoord(x,y)
                if new_pos.x>=0 and new_pos.x<self.width and new_pos.y>=0 and new_pos.y<self.height:
                    objects+=self.get_objects_in_cell(new_pos)
        return list(set(objects)) #remove identical objects
    
    def get_room_id(self,coord):
        return self.cells[coord.x][coord.y].room_id
    
    def make_walls_on_boundaries(self,cell_type_1,cell_type_2):
        for x in range(self.width):
            for y in range(self.height):
                on_cell=self.get_cell(MapCoord(x,y))
                for direction in range(4):
                    neighbor=self.get_cell(MapCoord(x,y)+MapCoord.direction_to_vector(Direction(direction)))
                    if neighbor is None:
                        continue
                    if on_cell.cell_type==cell_type_1 and neighbor.cell_type==cell_type_2:
                        on_cell.walls[direction].wall_type=WallType.WALL
                    if on_cell.cell_type==cell_type_2 and neighbor.cell_type==cell_type_1:
                        on_cell.walls[direction].wall_type=WallType.WALL

    def is_cell_visible(self,a,b):
        #trace a ray from a to be and see if it hits a wall
        acenter=(a[0]+0.5,a[1]+0.5)
        bcenter=(b[0]+0.5,b[1]+0.5)
        #print("checking visibility from {} to {}".format(acenter,bcenter))
        for x in range( min(a[0],b[0]),max(a[0],b[0])+1):
            for y in range( min(a[1],b[1]),max(a[1],b[1])+1):
                if self.cells[x][y].walls[0].wall_type in [WallType.WALL,WallType.DOOR_CLOSED]:
                    wall_start=(x,y)
                    wall_end=(x+1,y)
                    if intersect(acenter,bcenter,wall_start,wall_end):
                        return False
                if self.cells[x][y].walls[1].wall_type in [WallType.WALL,WallType.DOOR_CLOSED]:
                    wall_start=(x+1,y)
                    wall_end=(x+1,y+1)
                    if intersect(acenter,bcenter,wall_start,wall_end):
                        return False
                if self.cells[x][y].walls[2].wall_type in [WallType.WALL,WallType.DOOR_CLOSED]:
                    wall_start=(x,y+1)
                    wall_end=(x+1,y+1)
                    if intersect(acenter,bcenter,wall_start,wall_end):
                        return False
                if self.cells[x][y].walls[3].wall_type in [WallType.WALL,WallType.DOOR_CLOSED]:
                    wall_start=(x,y)
                    wall_end=(x,y+1)
                    if intersect(acenter,bcenter,wall_start,wall_end):
                        return False
                    
        return True
    
    def get_visible_cells(self,coord,distance=100):
        #visible_cells=[]
        #for x in range(coord[0]-distance,coord[0]+distance):
        #    for y in range(coord[1]-distance,coord[1]+distance):
        #        if self.is_on_map(MapCoord(x,y)) and self.is_cell_visible(coord,MapCoord(x,y)):
        #            visible_cells.append(MapCoord(x,y))

        #return visible_cells
        #returns a list of cells that are visible from the given cell
        #and a list of cells that are next to being visible fro the given cell
        visible_cells=[coord]
        open_cells=[coord]
        closed_cells=[]
        while len(open_cells)>0:
            cell=open_cells.pop(0)
            closed_cells.append(cell)
            for direction in range(4):
                new_cell=cell+MapCoord.direction_to_vector(Direction(direction))
                if self.is_on_map(new_cell) and self.is_cell_visible(coord,new_cell) and MapCoord(coord).manhattan_distance(MapCoord(new_cell)) < distance: 
                    if new_cell not in visible_cells:
                        visible_cells.append(new_cell)
                    if new_cell not in closed_cells and new_cell not in open_cells:
                        open_cells.append(new_cell)
                    else:
                        closed_cells.append(new_cell)
                else:
                    closed_cells.append(new_cell)
        nearby_cells=[ x for x in closed_cells if x not in visible_cells]
        return visible_cells,nearby_cells
    
    def get_objects_in_cells(self,coord_list):
        items=[]
        #print("getting objects in cells: "+str(coord_list))
        for coord in coord_list:
            items+=self.get_objects_in_cell(coord)
        return list(set(items)) #remove identical objects
    
    def get_objects_in_rect(self,rect):
        items=[]
        for x in range(rect[0],rect[0]+rect[2]):
            for y in range(rect[1],rect[1]+rect[3]):
                items+=self.get_objects_in_cell(MapCoord(x,y))
        return items
                    
    #def update_map_mask(self,map_mask,coord,distance=10):
        #update the map mask with the visible cells from the given cell
        #print("updating visiilib from cell: "+str(coord))
    #    visible_cells,nearby_cells=self.get_visible_cells(coord,distance)
    #    for cell in visible_cells:
    #        map_mask.set_visible(cell.x,cell.y)
    #    for cell in nearby_cells:
    #        map_mask.set_remembered(cell.x,cell.y)

    #lighting
    def set_ambient_light(self,level=255):
        #self.ambient_light=level
        for x in range(self.width):
            for y in range(self.height):
                self.cells[x][y].ambient_light_level=level

    def recalculate_object_lighting(self,object):
        if not object.needs_light_update and object.lighting_cells is not None:
            return object.lighting_cells
        object.needs_light_update=False
        #real light is 1/r^2
        #in 2d its 1/r
        #eye cells are more like logarithmic
        #let's try linear
   
        radius,intensity=object.get_lighting_params()
        lit_cells={} # ( (cell coord), light level)
        possibly_lit,nearby=self.get_visible_cells(object.get_pos(),radius)
        for cell in possibly_lit:
                distance=cell.manhattan_distance(object.get_pos())
                if distance<1:
                    distance=1
                if distance<radius:
                    intensity_at_distance=intensity*(1-distance/radius)
                    lit_cells[cell ]=intensity_at_distance
        object.lighting_cells=lit_cells
        return lit_cells

    def recalculate_lighting(self,rect=None):
        if rect is None:
            rect=[0,0,self.width,self.height]
        for x in range(rect[0],rect[0]+rect[2]):
            for y in range(rect[1],rect[1]+rect[3]):
                self.cells[x][y].light_level=self.cells[x][y].ambient_light_level
        objects=self.get_objects_in_rect(rect)
        for obj in objects:
            radius,intensity=obj.get_lighting_params()
            if intensity>0:
                lit_cells=self.recalculate_object_lighting(obj)
                for x in range(rect[0],rect[0]+rect[2]):
                    for y in range(rect[1],rect[1]+rect[3]):
                        if MapCoord(x,y) in lit_cells:
                            self.cells[x][y].light_level+=lit_cells[MapCoord(x,y)]
        for x in range(rect[0],rect[0]+rect[2]):
            for y in range(rect[1],rect[1]+rect[3]):
                self.cells[x][y].light_level=int(clip(self.cells[x][y].light_level,0,255))
