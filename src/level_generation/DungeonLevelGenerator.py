import random
from ..level.LevelData import LevelData
from ..level.MapCoord import MapCoord
from ..level.ObjectStore import ObjectStore
from ..level.GraphPaperMap import GraphPaperMap, CellType
from ..level.ObjectFactory import create_object_from_template
from ..level.MapRoom import MapRoom
from .AStarAlgorithm import DigPathThroughStone
from .Network import Network
from ..behavior.BasicBehaviors import *

class DungeonLevelGenerator:
    def __init__(self):
        ...

    def generate(self,xsize,ysize,name):
        print("Generating dungeon level")
        level=LevelData()
        level.map=GraphPaperMap(xsize,ysize)
        level.level_name=name

        self.generate_map(level)
       
        return level
    
    def generate_map(self,level):
        map=level.map
        center_x=int(map.width/2)
        center_y=int(map.height/2)

        #let's try the room subdivision algorithm
        my_rect=[3,3,map.width-6,map.height-6]
        my_rects=self.recursive_subdivide([my_rect])

        level.map.fill(None,CellType.STONE)

        rooms=[]
        for rect in my_rects:
            room=MapRoom(rect)
            room.create_exits(2)
            room.dig_self_on_map(level.map)
            rooms.append(room)

        #build a minimal spanning tree
        network=Network.fully_connected_network(len(rooms))
        network.prune_until_spanning_tree()
        for edge in network.edges:
            room1=rooms[edge[0]]
            room2=rooms[edge[1]]
            start=MapCoord(room1.get_center())
            finish=MapCoord(room2.get_center())
            #print("connecting",start,finish )
            path=DigPathThroughStone(level.map).find_path(start,finish)
            #print("path is ",path)
            if path is not None:
                for coord in path:
                    level.map.cells[coord.x][coord.y].cell_type=CellType.DIRT

        #put walls up where relevant
        level.map.make_walls_on_boundaries(CellType.STONE,CellType.DIRT)

        center_x=rooms[0].rect[0]+rooms[0].rect[2]//2
        center_y=rooms[0].rect[1]+rooms[0].rect[3]//2

        #add some monsters
        centerx2=rooms[1].rect[0]+rooms[1].rect[2]//2
        centery2=rooms[1].rect[1]+rooms[1].rect[3]//2
        monster=create_object_from_template("imp")
        #monster.behavior=BTRandomWalk()
        monster.behavior=BTChasePlayer()


        level.add_object_to_cell(monster,MapCoord(centerx2,centery2))

        level.player_respawn_point=MapCoord(center_x,center_y)
        level.tileset_name="dungeon"
        


# for creating rooms with the division method
    def recursive_subdivide(self,rectlist):
        ret=[]
        for rect in rectlist:
            sub_list=self.subdivide(rect)
            if sub_list is not None:
                ret.extend(self.recursive_subdivide(sub_list))
            else:
                ret.append(rect)
        return ret

    def subdivide(self,rect):
        #print("subdivide",rect)
        min_size=3 # the smallest dimension a room can be
        padding=3 # the minimum distance between rooms
        if rect[2]>rect[3]: 
            #split vertically
            if rect[2]<min_size*2+padding:
                return None
            split=random.randint(min_size,rect[2]-min_size-padding)
            rect1=[rect[0],rect[1],split,rect[3]]
            rect2=[rect[0]+split+padding,rect[1],rect[2]-split-padding,rect[3]]
            return [rect1,rect2]
        else:
            #split horizontally
            if rect[3]<min_size*2+padding:
                return None
            split=random.randint(min_size,rect[3]-min_size-padding)
            rect1=[rect[0],rect[1],rect[2],split]
            rect2=[rect[0],rect[1]+split+padding,rect[2],rect[3]-split-padding]
            return [rect1,rect2]
        
    