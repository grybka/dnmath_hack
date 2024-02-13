import random
from ..level.LevelData import LevelData
from ..level.MapCoord import MapCoord
from ..level.ObjectStore import ObjectStore
from ..level.GraphPaperMap import GraphPaperMap, CellType, MapMask
from ..level.MapRoom import *
from ..behavior.BehaviorTree import BehaviorTreeSelector
from ..behavior.BasicBehaviors import *
from ..level.ObjectFactory import create_object_from_template

from .LevelGenerator import LevelGenerator

class OutdoorLevelGenerator(LevelGenerator):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.info=kwargs
        
        
    def generate(self):
        print("Generating outdoor level")

        self.generate_map(self.level)

        return self.level

    def generate_map(self,level):
        map=level.map
        center_x=int(map.width/2)
        center_y=int(map.height/2)

        #call the outside a room - key is "outside"
        #impassible border not included
        outside_room=MapRoom([1,1,map.width-2,map.height-2],"outside")
        level.room_store.add_room(outside_room)
        map.set_room("outside")

        #add some trees
        #n_trees=10
        #for i in range(n_trees):
        #    x=random.randint(1,map.width-2)
        #    y=random.randint(1,map.height-2)
        #    if map.get_cell_type(MapCoord(x,y))==CellType.OUTDOOR_GRASS:
        #        obj=create_object_from_template("tree_2")
        #        level.add_object_to_cell(obj,MapCoord(x,y))

        #add some items for tests
        #items_to_add=["dagger","barrel","spear"]
        
        #for item in items_to_add:
        #    obj=create_object_from_template(item)
        #    x=random.randint(1,map.width-2)
        #    y=random.randint(1,map.height-2)
        #    level.add_object_to_cell(obj,MapCoord(x,y))


        #make impassible border
        for i in range(map.width):
            map.set_cell_type(MapCoord(i,0),CellType.IMPASSIBLE)
            map.set_cell_type(MapCoord(i,map.height-1),CellType.IMPASSIBLE)
        for i in range(map.height):
            map.set_cell_type(MapCoord(0,i),CellType.IMPASSIBLE)
            map.set_cell_type(MapCoord(map.width-1,i),CellType.IMPASSIBLE)


        #lighting
        map.set_ambient_light(255)
        map.recalculate_lighting()
        level.memory_mask=MapMask(map.width,map.height)

        #add buildings

        self.make_areas(level,outside_room)

        self.add_portals(level)
        

        self.add_furnishings(level)
        #add enemies
        #self.add_enemies(level)

        #make an exit
        #exit_room=MRExit([center_x-1,0,1,1],None,None)
        #exit_room.dig_self_on_map(map)
        #level.room_store.add_room(exit_room)
        

        #level.player_respawn_point=MapCoord(center_x,center_y)
        level.tileset_name="outdoor"
        return level
    
    
    

    def add_enemies(self,level):
        #add some enemies
        map=level.map
        enemies_to_add=["imp","skeleton","skeleton"]
        for enemy in enemies_to_add:
            obj=create_object_from_template(enemy)
            #obj.behavior=BTChasePlayer()
            #obj.behavior=BTRandomWalk()
            #obj.behavior=BTRangedAttackPlayer()
            if enemy=="skeleton":
                obj.behavior=BehaviorTreeSelector([BTMeleeAttackPlayer(),BTChasePlayer()])
            if enemy=="imp":
                obj.behavior=BehaviorTreeSelector([BTRangedAttackPlayer(),BTChasePlayer()])
            coord=self.choose_random_square_of_type(CellType.OUTDOOR_GRASS)
            if coord is not None:
                level.add_object_to_cell(obj,coord)

    def make_areas(self,level,outside_room):
        if "areas" not in self.info:
            return
        for area,area_info in self.info["areas"].items():
            
            if "type" not in area_info or area_info["type"]!="building":
                continue

            #build a house
            coord=area_info["coord"]
            rect=area_info["rect"]

            house=MapRoom([coord[0],coord[1],rect[0],rect[1]],parent=outside_room,id=area)
            outside_room.children.append(house)
            if "exits" in area_info:
                for exit in area_info["exits"]:
                    house.create_exits(1,has_doors=True)
                    #house.create_double_exit()

            map=level.map

            house.dig_self_on_map(map)
            house.clear_of_objects(level)

            house.build_walls(map)
            house.set_lighting(map,130)
            level.room_store.add_room(house)

            #add any furnishings
            if "furnishings" in area_info:
                for furnishing in area_info["furnishings"]:
                    self.add_furnishing(level,house,furnishing)

    def add_furnishing(self,level,room,furnishing):
        coord=MapCoord(0,0)
        if "relative_coord" in furnishing:
            coord=room.get_relative_coord(MapCoord(furnishing["relative_coord"]))
        print("creating furnishing at ",coord,furnishing["type"])
        obj=create_object_from_template(furnishing["type"],furnishing.get("object_data",{}))
        level.add_object_to_cell(obj,coord)


