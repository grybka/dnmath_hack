from collections import deque
from .EngineMessage import EngineMessage
from ..level.LevelData import LevelData,LevelStore
from ..level.ObjectFactory import create_object_from_template
from ..level.GameObject import GameObject
from ..level.Entity import Entity

class GameEngine:
    def __init__(self):
        self.messages=[]
        self.level_store=LevelStore()
        self.level=None
        self.player_id=None
        self.player_action=None
        self.entities_to_remove=[]

    def add_level(self,level:LevelData):
        self.level_store.levels[level.level_name]=level
        if self.level is None:
            self.level=level
    
    #this creates the player object
    def spawn_player(self):
        player=create_object_from_template("player")
        self.player_id=player.id
        dagger=create_object_from_template("dagger")
        bow=create_object_from_template("bow")
        self.level.object_store.add_object(dagger)
        self.level.object_store.add_object(bow)
        player.inventory.append(dagger)
        player.inventory.append(bow)
        player.equip_item(bow)
        self.level.add_object_to_cell(player,self.level.player_respawn_point)

    def get_player(self):
        return self.level.object_store.get_object(self.player_id)

    def add_message(self,message:EngineMessage):
        self.messages.append(message)

    def messages_pending(self):
        return len(self.messages)>0
    
    def pop_message(self):
        return self.messages.pop(0)

    def set_player_action(self,action):
        self.player_action=action

    def schedule_entity_removal(self,entity:Entity):
        self.entities_to_remove.append(entity)

    def update_timestep(self):
        #remove any entities that must be removed
        if len(self.entities_to_remove)>0:
            for entity in self.entities_to_remove:
                self.level.delete_object(entity)
            self.entities_to_remove=[]
        #TODO figure out who's turn it is
        #act if it is the players turn
        if self.player_action is None:
            return
        else:
            self.player_action.execute_if_possible()
            self.player_action=None
            return

        ...