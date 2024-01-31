import random
from ..level.MapCoord import MapCoord
from ..level.GraphPaperMap import GraphPaperMap, CellType, WallType

class MapRoom:
    def __init__(self,rect):
        self.rect=rect #[x,y,width,height] with x,y being the upper left
        self.exits=[]

    def choose_edge(self):
        side=random.randint(0,3)
        if side==0:
            return [random.randint(self.rect[0],self.rect[0]+self.rect[2]-1),self.rect[1],0]
        if side==1:
            return [self.rect[0]+self.rect[2]-1,random.randint(self.rect[1],self.rect[1]+self.rect[3]-1),1]
        if side==2:
            return [random.randint(self.rect[0],self.rect[0]+self.rect[2]-1),self.rect[1]+self.rect[3]-1,2]
        if side==3:
            return [self.rect[0],random.randint(self.rect[1],self.rect[1]+self.rect[3]-1),3]

    def create_exits(self,n_exits):
        for i in range(n_exits):
            self.exits.append(self.choose_edge())

    def get_center(self):
        return [self.rect[0]+self.rect[2]//2,self.rect[1]+self.rect[3]//2]
            

    def dig_self_on_map(self,map):
        #remove the stone
        map.fill(self.rect,CellType.DIRT)
        #build the walls
        for x in range(self.rect[0],self.rect[0]+self.rect[2]):
            #North Wall
            if [x,self.rect[1],0] not in self.exits:
                map.get_wall(MapCoord(x,self.rect[1]),0).wall_type=WallType.WALL
                if map.get_opposite_wall(MapCoord(x,self.rect[1]),0) is not None:
                    map.get_opposite_wall(MapCoord(x,self.rect[1]),0).wall_type=WallType.WALL
            #South Wall
            if [x,self.rect[1]+self.rect[3]-1,2] not in self.exits:
                map.get_wall(MapCoord(x,self.rect[1]+self.rect[3]-1),2).wall_type=WallType.WALL
                if map.get_opposite_wall(MapCoord(x,self.rect[1]+self.rect[3]-1),2) is not None:
                    map.get_opposite_wall(MapCoord(x,self.rect[1]+self.rect[3]-1),2).wall_type=WallType.WALL

        for y in range(self.rect[1],self.rect[1]+self.rect[3]):
            #West Wall
            if [self.rect[0],y,3] not in self.exits:
                map.get_wall(MapCoord(self.rect[0],y),3).wall_type=WallType.WALL
                if map.get_opposite_wall(MapCoord(self.rect[0],y),3) is not None:
                    map.get_opposite_wall(MapCoord(self.rect[0],y),3).wall_type=WallType.WALL
            #East Wall
            if [self.rect[0]+self.rect[2]-1,y,1] not in self.exits:
                map.get_wall(MapCoord(self.rect[0]+self.rect[2]-1,y),1).wall_type=WallType.WALL
                if map.get_opposite_wall(MapCoord(self.rect[0]+self.rect[2]-1,y),1) is not None:
                    map.get_opposite_wall(MapCoord(self.rect[0]+self.rect[2]-1,y),1).wall_type=WallType.WALL
