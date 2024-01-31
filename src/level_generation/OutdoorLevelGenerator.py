import random
from ..level.LevelData import LevelData
from ..level.MapCoord import MapCoord
from ..level.ObjectStore import ObjectStore
from ..level.GraphPaperMap import GraphPaperMap, CellType
from ..level.ObjectFactory import create_object_from_template

class OutdoorLevelGenerator:
    def __init__(self):
        ...
        
        
    def generate(self,xsize,ysize,name):
        print("Generating outdoor level")
        level=LevelData()
        level.map=GraphPaperMap(xsize,ysize)
        level.level_name=name

        self.generate_map(level)

        return level

    def generate_map(self,level):
        map=level.map
        center_x=int(map.width/2)
        center_y=int(map.height/2)

        #add some trees
        n_trees=10
        for i in range(n_trees):
            x=random.randint(1,map.width-2)
            y=random.randint(1,map.height-2)
            if map.get_cell_type(MapCoord(x,y))==CellType.DIRT:
                obj=create_object_from_template("tree_2")
                level.add_object_to_cell(obj,MapCoord(x,y))

        #add some items for tests
        items_to_add=["dagger","barrel","spear"]
        for item in items_to_add:
            obj=create_object_from_template(item)
            x=random.randint(1,map.width-2)
            y=random.randint(1,map.height-2)
            level.add_object_to_cell(obj,MapCoord(x,y))

        #add some enemies
        enemies_to_add=["imp","skeleton","skeleton"]
        for enemy in enemies_to_add:
            obj=create_object_from_template(enemy)
            x=random.randint(1,map.width-2)
            y=random.randint(1,map.height-2)
            level.add_object_to_cell(obj,MapCoord(x,y))

        #make impassible border
        for i in range(map.width):
            map.set_cell_type(MapCoord(i,0),CellType.IMPASSIBLE)
            map.set_cell_type(MapCoord(i,map.height-1),CellType.IMPASSIBLE)
        for i in range(map.height):
            map.set_cell_type(MapCoord(0,i),CellType.IMPASSIBLE)
            map.set_cell_type(MapCoord(map.width-1,i),CellType.IMPASSIBLE)


        level.player_respawn_point=MapCoord(center_x,center_y)
        level.tileset_name="outdoor"
        return level