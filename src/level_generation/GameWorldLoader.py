import yaml
from .OutdoorLevelGenerator import OutdoorLevelGenerator
from .DungeonLevelGenerator import DungeonLevelGenerator

class GameWorldLoader:
    def __init__(self):
        self.levels={}
        self.level_info={}

    def load_gameworld_file(self,fname):
        with open(fname, 'r') as file:
            self.game_info = yaml.safe_load(file)["gameworld"]
        self.globals=self.game_info.get("global",{})
        self.level_info=self.game_info.get("levels",{})

    def get_level(self,level_name):
        if level_name not in self.levels:
            if level_name not in self.level_info:
                raise Exception("Level {} not found".format(level_name))
            this_level_info=self.level_info[level_name]
            self.levels[level_name]=self.generate(this_level_info) 
        return self.levels[level_name]
    
    #where should the player start when the game first begins
    def get_player_start(self):
        #return level_name, entry_point
        print("Game info ",self.game_info)
        print("Globals: ",self.globals)
        return self.globals.get("start_level",""),self.globals.get("start_entry_point","")

    #given the player exited from exit name on from_level level, which level and entry point should they go to?
    def get_level_transition(self,from_level,exit_name):
        #return level_name, entry_point
        level=self.level_info.get(from_level,{})
        exit=level.portals[exit_name]
        next_level=exit.get("next_level",None)
        next_entry=exit.get("next_entry_point",None)
        return next_level,next_entry
    
    def generate(self,level_info):
        #given a level_info dictionary, generate the level
        if level_info["generator"]=="outdoor":
            generator=OutdoorLevelGenerator(**level_info)
            return generator.generate()
        if level_info["generator"]=="dungeon":
            generator=DungeonLevelGenerator(**level_info)
            return generator.generate()
        raise Exception("Unknown level generator {}".format(level_info["generator"]))