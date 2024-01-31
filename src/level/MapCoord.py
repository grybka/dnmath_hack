from enum import Enum

class Direction(Enum):
    N=0
    E=1
    S=2
    W=3

    def __int__(self):
        return self.value

class MapCoord:
    def __init__(self,*params):
        if len(params)==1:
            self.x=int(params[0][0])
            self.y=int(params[0][1])
        else:
            self.x=int(params[0])
            self.y=int(params[1])
    def __eq__(self,other):
        return self.x==other.x and self.y==other.y
    def __ne__(self,other):
        return not self.__eq__(other)
    def __hash__(self):
        return hash((self.x,self.y))
    def __str__(self):
        return "MapCoord("+str(self.x)+","+str(self.y)+")"
    def __repr__(self):
        return self.__str__()
    def __add__(self,other):
        return MapCoord(self.x+other.x,self.y+other.y)
    def __sub__(self,other):
        return MapCoord(self.x-other.x,self.y-other.y)
    def __mul__(self,other):
        return MapCoord(self.x*other,self.y*other)
    def __getitem__(self,index):
        if index==0:
            return self.x
        if index==1:
            return self.y
        raise Exception("Invalid index")
    def manhattan_distance(self,other):
        return abs(self.x-other.x)+abs(self.y-other.y)
    def rotated_left(self):
        return MapCoord(-self.y,self.x)
    def rotated_right(self):
        return MapCoord(self.y,-self.x)
    def rotated_180(self):
        return MapCoord(-self.x,-self.y)
    @staticmethod
    def direction_to_vector(direction):
        if direction==Direction.N:
            return MapCoord(0,-1)
        if direction==Direction.S:
            return MapCoord(0,1)
        if direction==Direction.E:
            return MapCoord(1,0)
        if direction==Direction.W:
            return MapCoord(-1,0)
        if direction==0:
            return MapCoord(0,-1)
        if direction==1:
            return MapCoord(1,0)
        if direction==2:
            return MapCoord(0,1)
        if direction==3:
            return MapCoord(-1,0)
        raise Exception("Unknown direction: "+str(direction))
    
def opposite_dir(dir):
    if dir==Direction.N:
        return Direction.S
    if dir==Direction.S:
        return Direction.N
    if dir==Direction.E:
        return Direction.W
    if dir==Direction.W:
        return Direction.E
    if dir==0:
        return Direction.S
    if dir==1:
        return Direction.W
    if dir==2:
        return Direction.N
    if dir==3:
        return Direction.E
    
def left_of(dir):
    if dir==Direction.N:
        return Direction.W
    if dir==Direction.S:
        return Direction.E
    if dir==Direction.E:
        return Direction.N
    if dir==Direction.W:
        return Direction.S
    
def right_of(dir):
    if dir==Direction.N:
        return Direction.E
    if dir==Direction.S:
        return Direction.W
    if dir==Direction.E:
        return Direction.S
    if dir==Direction.W:
        return Direction.N