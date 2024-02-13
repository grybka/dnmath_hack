from collections import deque
from .EngineMessage import *
from ..level.LevelData import LevelData,LevelStore
from ..level.ObjectFactory import create_object_from_template
from ..level.GameObject import GameObject
from ..level.Entity import Entity

class GameEngine:
    def __init__(self,world_loader):
        self.messages=[]
#        self.level_store=LevelStore()
        self.world_loader=world_loader
        self.level=None
        self.player_id=None
        #self.player_action=None
        self.entity_actions={}
        self.entities_to_remove=[]
        self.scheduled_level_change=None
        start_level,entry_point=self.world_loader.get_player_start()
        self.set_level(start_level)
        self.spawn_player(entry_point)
#        self.level=world_loader.get_level(world_loader.get_starting_level())

    def add_level(self,level:LevelData):
        self.level_store.levels[level.level_name]=level
        if self.level is None:
            self.set_level(level.level_name)
            
    def set_level(self,level_name):
        #self.level=self.level_store.levels[level_name]
        self.level=self.world_loader.get_level(level_name)
        print("self level ",self.level)
        self.level.reset_initiative()
    
    #this creates the player object
    def spawn_player(self,entry_point):
        player=create_object_from_template("player")
        self.player_id=player.id
        dagger=create_object_from_template("dagger")
        bow=create_object_from_template("bow")
        torch=create_object_from_template("holding_torch")
        self.level.object_store.add_object(dagger)
        self.level.object_store.add_object(bow)
        self.level.object_store.add_object(torch)
        player.inventory.append(dagger)
        player.inventory.append(bow)
        player.inventory.append(torch)
        player.equip_item(bow)
        player.equip_item(torch)

        coord=self.level.get_entry_point_location(entry_point)

        self.level.add_object_to_cell(player,coord)
        self.update_lighting_and_visibilility()

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

    def schedule_level_change(self,exit_pos):
        exit_portal=self.level.get_exit_portal(exit_pos)
        level_name=exit_portal.target_level
        spawn_point=exit_portal.target_entry_point
        if exit_portal.type=="stairs_up":
            self.add_message(EMInfoText("You ascend the stairs"))
        if exit_portal.type=="stairs_down":
            self.add_message(EMInfoText("You descend the stairs"))
#        level_name,spawn_point=self.level.get_exit_destination(exit_pos)
        self.scheduled_level_change=(level_name,spawn_point)

    def update_timestep(self):
        #remove any entities that must be removed
        if len(self.entities_to_remove)>0:
            for entity in self.entities_to_remove:
                self.level.delete_object(entity)
            self.entities_to_remove=[]
        #figure out if its time to chang elevel
        if self.scheduled_level_change is not None:
            level_name,spawn_point=self.scheduled_level_change
            player=self.get_player()
            self.level.delete_object(player)
            self.set_level(level_name)
            #print("spawn point is {}".format(spawn_point))
            spawn_coord=self.level.get_entry_point_location(spawn_point)
            self.level.add_object_to_cell(player,spawn_coord)
            self.scheduled_level_change=None
            self.update_lighting_and_visibilility()
            self.add_message(EMLevelChanged(self.level,level_name))
            in_room=self.level.get_room_at(spawn_coord)
            self.add_message(EMRoomChanged(player.id,None,in_room,in_room.description))

            return 

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
                #print("no action for {}".format(entity.reference_noun()))
                self.level.add_to_entity_initiative(entity_id,1.0)
                return
        the_action.execute_if_possible()
        #I guess everytime I do something, recalculate the map lighting and player visibility?
        self.update_lighting_and_visibilility()

    def update_lighting_and_visibilility(self):
        self.level.map.recalculate_lighting()
        self.level.memory_mask.visible_to_remembered()
        visible_cells=self.get_player().get_visible_cells(self.level.map)
        neighbor_cells=[]
        #get all cells adjacent to visible cells
        for cell in visible_cells:
            for neighbor in cell.get_neighbors():
                if neighbor not in visible_cells:
                    neighbor_cells.append(neighbor)
        for cell in visible_cells:
            self.level.memory_mask.set_visible(cell.x,cell.y)
        for cell in neighbor_cells:
            self.level.memory_mask.set_remembered(cell.x,cell.y)


        