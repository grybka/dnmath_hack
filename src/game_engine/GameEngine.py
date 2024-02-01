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
        #self.player_action=None
        self.entity_actions={}
        self.entities_to_remove=[]

    def add_level(self,level:LevelData):
        self.level_store.levels[level.level_name]=level
        if self.level is None:
            self.set_level(level.level_name)
            
    def set_level(self,level_name):
        self.level=self.level_store.levels[level_name]
        self.level.reset_initiative()
    
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
        #self.player_action=action
        self.entity_actions[self.player_id]=action

    def set_entity_action(self,entity_id,action):
        self.entity_actions[entity_id]=action

    def get_entity_action(self,entity_id):
        if entity_id in self.entity_actions:
            ret=self.entity_actions[entity_id]
            self.entity_actions[entity_id]=None
            return ret
        return None
    
    def schedule_entity_removal(self,entity:Entity):
        self.entities_to_remove.append(entity)

    def update_timestep(self):
        #remove any entities that must be removed
        if len(self.entities_to_remove)>0:
            for entity in self.entities_to_remove:
                self.level.delete_object(entity)
            self.entities_to_remove=[]
        #figure out who's turn it is
        entity_id=self.level.get_next_entity_in_initiative()
        entity=self.level.object_store.get_object(entity_id)
        if entity.behavior is not None:
            entity.behavior.act(entity,self)
        the_action=self.get_entity_action(entity_id)
        if the_action is None:
            if entity_id==self.player_id:
                return #The player has to input an action, wait
            else:
                #The entity's ai failed to produce an action, wait by default
                print("no action for {}".format(entity.reference_noun()))
                self.level.add_to_entity_initiative(entity_id,1.0)
                return
        the_action.execute_if_possible()
        #I guess everytime I do something, recalculate the map lighting and player visibility?
        self.level.map.recalculate_lighting()
        self.level.memory_mask.visible_to_remembered()
        visible_cells,nearby_cells=self.get_player().get_visible_cells(self.level.map,include_nearby=True)
        for cell in visible_cells:
            self.level.memory_mask.set_visible(cell.x,cell.y)
        for cell in nearby_cells:
            self.level.memory_mask.set_remembered(cell.x,cell.y)



        