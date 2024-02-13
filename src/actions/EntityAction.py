from ..game_engine.GameEngine import GameEngine
from ..game_engine.EngineMessage import *
from ..level.GameObject import GameObject,GameObjectContainer
from ..level.WallObject import DoorObject
from ..level.Entity import Entity
from ..level.MapCoord import Direction,MapCoord
from ..level.GraphPaperMap import CellType


class EntityAction:
    def __init__(self,name,actor:Entity,engine:GameEngine,**kwargs):
        self.name=name #the word describing the action
        self.actor=actor
        self.engine=engine

    def is_possible(self):
        return False, "Action Base Class"

    def execute(self):
        ...

    def execute_if_possible(self):
        possible,message=self.is_possible()
        if possible:
            self.execute()
        else:
            self.engine.add_message(EMActionFailed(message))
            if self.actor is not None: #by default, failing means you lose your turn
                self.engine.level.add_to_entity_initiative(self.actor.id,1.0)

class WaitAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine):
        super().__init__("wait",actor,engine)

    def is_possible(self):
        return True, "Can wait"
    
    def execute(self):
        self.engine.add_message(EMInfoText("You wait"))
        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)

class MoveAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,direction:Direction):
        super().__init__("move",actor,engine)
        self.direction=direction

    def execute(self):
        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)
        level=self.actor.get_level()
        old_pos=self.actor.get_pos()
        new_pos=self.actor.get_pos()+MapCoord.direction_to_vector(self.direction)
        old_room=level.get_room_at(old_pos)
        new_room=level.get_room_at(new_pos)
        #Special case - exits to other levels
        if level.map.get_cell(new_pos).cell_type==CellType.EXIT:
            self.engine.schedule_level_change(new_pos)


        level.map.remove_object_from_cell(self.actor,self.actor.get_pos())
        level.map.add_object_to_cell(self.actor,new_pos)
        if new_room != old_room:
            self.engine.add_message(EMRoomChanged(self.actor.id,old_room,new_room,new_room.description))
        self.engine.add_message(EMObjectMoved(self.actor.id,old_pos,new_pos))

    def is_possible(self):
        level=self.actor.get_level()
        if self.actor.get_pos() is None:
            return False, "Actor has no location"
        if not level.map.is_passable(self.actor.get_pos(),self.direction,self.actor.passable_cells):
            return False, "You cannot go that way"
        new_pos=self.actor.get_pos()+MapCoord.direction_to_vector(self.direction)
        for object in level.map.get_objects_in_cell(new_pos):
            if object.block_movement:
                return False, "There is something in your way"
        return True, "You may move"
    
class TakeAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,object:GameObject):
        super().__init__("take",actor,engine)
        self.object=object

    def is_possible(self):
        if self.object is None:
            return False, "No object to take."
        if not self.object.is_takable:
            return False, "You can't take {}".format(self.object.reference_noun(specific=False))
        if self.object.get_pos() is None:
            return False, "Object is not on the map"
        if self.actor.get_pos().manhattan_distance(self.object.get_pos())>1:
            return False, "Object is too far away."
        return True, "Can take"
    
    def execute(self):
        level=self.actor.get_level()
        level.map.remove_object_from_cell(self.object,self.object.get_pos())
        self.actor.inventory.append(self.object)
        self.engine.add_message(EMInfoText("You take "+self.object.reference_noun(specific=True)))
        self.engine.add_message(EMMapChanged())
        self.engine.add_message(PlayerInventoryChanged())
        #self.engine.add_message(EMObjectTaken(self.actor.id,self.object.id))

class DropAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,object:GameObject):
        super().__init__("drop",actor,engine)
        self.object=object

    def is_possible(self):
        if self.object is None:
            return False, "No object to drop."
        if not self.object in self.actor.inventory:
            return False, "You don't have {}".format(self.object.reference_noun(specific=False))
        #if not self.object.is_takable:
        #    return False, "You can't take {}".format(self.object.reference_noun(specific=False))
        #if self.actor.get_pos().manhattan_distance(self.object.get_pos())>1:
        #    return False, "Object is too far away."
        return True, "Can drop"
    
    def execute(self):
        level=self.actor.get_level()
        #unequip if equipped
        self.actor.unequip_item(self.object)
        self.actor.inventory.remove(self.object)
        level.map.add_object_to_cell(self.object,self.actor.get_pos())
        self.engine.add_message(EMInfoText("You drop "+self.object.reference_noun(specific=True)))
        #self.engine.add_message(EMMapChanged())
        self.engine.add_message(PlayerInventoryChanged())

#Equip
class EquipAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,object:GameObject):
        super().__init__("equip",actor,engine)
        self.object=object

    def is_possible(self):
        if self.object is None:
            return False, "No object to drop."
        if not self.object in self.actor.inventory:
            return False, "You don't have {}".format(self.object.reference_noun(specific=False))
        slot=self.actor.get_equipped_slot(self.object)
        if slot is not None:
            return False, "You already have {} equipped".format(self.object.reference_noun(specific=False))
        #if not self.object.is_takable:
        #    return False, "You can't take {}".format(self.object.reference_noun(specific=False))
        #if self.actor.get_pos().manhattan_distance(self.object.get_pos())>1:
        #    return False, "Object is too far away."
        return True, "Can equip"
    
    def execute(self):
        level=self.actor.get_level()
        self.actor.equip_item(self.object)
        level.map.recalculate_lighting()

        self.engine.add_message(EMInfoText("You equip "+self.object.reference_noun(specific=True)))
        #self.engine.add_message(EMMapChanged())
        self.engine.add_message(PlayerInventoryChanged())


#Unequip
class UnequipAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,object:GameObject):
        super().__init__("unequip",actor,engine)
        self.object=object

    def is_possible(self):
        if self.object is None:
            return False, "No object to unequip."
        if not self.object in self.actor.inventory:
            return False, "You don't have {}".format(self.object.reference_noun(specific=False))
        slot=self.actor.get_equipped_slot(self.object)
        if slot is None:
            return False, "You don't have {} equipped".format(self.object.reference_noun(specific=False))
        #if not self.object.is_takable:
        #    return False, "You can't take {}".format(self.object.reference_noun(specific=False))
        #if self.actor.get_pos().manhattan_distance(self.object.get_pos())>1:
        #    return False, "Object is too far away."
        return True, "Can unequip"
    
    def execute(self):
        level=self.actor.get_level()
        self.actor.unequip_item(self.object)
        level.map.recalculate_lighting()

        self.engine.add_message(EMInfoText("You unequip "+self.object.reference_noun(specific=True)))
        self.engine.add_message(EMMapChanged())
        self.engine.add_message(PlayerInventoryChanged())

#Melee attack
class MeleeAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,target:Entity):
        super().__init__("Melee",actor,engine)
        self.target=target

    def is_possible(self):
        if self.target is None:
            return False, "No target to attack"
        if self.target.get_pos() is None:
            return False, "Target has no location"
        if self.actor.get_pos().manhattan_distance(self.target.get_pos())>1:
            return False, "Target is too far away."
        if not isinstance(self.target,Entity):
            return False, "Target is not an attackable"
        if self.actor.get_melee_weapon() is None:
            return False, "You have no means of attack"
        return True, "Can attack"
    
    def execute(self):
        #figure out what I'm attacking with
        weapon=self.actor.get_melee_weapon()
        damage=weapon.attack_info.damage
        if self.actor==self.engine.get_player():
            text=weapon.attack_info.get_your_attack_message(self.actor,self.target)
        else:
            text=weapon.attack_info.get_enemy_attack_message(self.actor,self.target)

        #subtract damage from target
        self.target.hp-=damage
        #TODO if target is dead, remove from maps
        #send out messages
        self.engine.add_message(EMMeleeAttack(self.actor.id,self.target.id,damage,text))
        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)
        if self.target.hp<=0:
            self.engine.add_message(EMCreatureDeath(self.target,self.target.get_pos()))
            self.target.dead=True
            #TODO should there be a more general way to do this?
            self.engine.schedule_entity_removal(self.target)

class RangedAttackAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,target:Entity):
        super().__init__("Missile",actor,engine)
        self.target=target

    def is_possible(self):
        if self.target is None:
            return False, "No target to attack"
        weapon=self.actor.get_missile_weapon()

        if weapon is None:
            return False, "You have no missile weapon"
        if weapon.attack_info is None:
            return False, "Your missile weapon cannot be used for ranged attacks"
        #TODO ammo
        range=weapon.attack_info.range
        if self.target.get_pos() is None:    
            return False, "Target has no location"
        if self.actor.get_pos().manhattan_distance(self.target.get_pos())>range:
            return False, "Target is too far away."
        if not isinstance(self.target,Entity):
            return False, "Target is not an attackable"
        return True, "Can attack"
    
    def execute(self):
        #TODO start here
        #figure out what I'm attacking with
        weapon=self.actor.get_missile_weapon()
        damage=weapon.attack_info.damage
        if self.actor==self.engine.get_player():
            text=weapon.attack_info.get_your_attack_message(self.actor,self.target)
        else:
            text=weapon.attack_info.get_enemy_attack_message(self.actor,self.target)
        #subtract damage from target
        self.target.hp-=damage
        #TODO if target is dead, remove from maps
        #send out messages
        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)
        self.engine.add_message(EMRangedAttack(self.actor.id,self.target.id,damage,text,"arrow",self.actor.get_pos(),self.target.get_pos()))
        if self.target.hp<=0:
            self.engine.add_message(EMCreatureDeath(self.target,self.target.get_pos()))
            self.target.dead=True
            #TODO should there be a more general way to do this?
            self.engine.schedule_entity_removal(self.target)

class ReadAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,object:GameObject):
        super().__init__("read",actor,engine)
        self.object=object

    def is_possible(self):
        if self.object is None:
            return False, "No object to read."
        if self.object.read_message is None:
            return False, "You can't read {}".format(self.object.reference_noun(specific=False))
        #if self.object.get_pos() is None:
        #    return False, "Object is not on the map"
        if self.object.get_pos() is None:
            if self.object not in self.actor.inventory:
                return False, "You don't have {}".format(self.object.reference_noun(specific=False))
        else:
            if self.actor.get_pos().manhattan_distance(self.object.get_pos())>1:
                return False, "Object is too far away."
        return True, "Can read"
    
    def execute(self):
        self.engine.add_message(EMInfoText("You read "+self.object.reference_noun(specific=True)))
        self.engine.add_message(EMReadMessage(self.object.id,self.actor.id,self.object.read_message))
    
class OpenDoorAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,door:GameObject):
        super().__init__("open",actor,engine)
        self.door=door

    def is_possible(self):
        if self.door is None:
            return False, "No door to open."
        if not isinstance(self.door,DoorObject):
            return False, "That is not a door"
        if self.door.get_pos() is None:
            return False, "Door is not on the map"
        #see if door is adjacent to actor
        if self.door not in self.engine.level.map.get_objects_in_cell(self.actor.get_pos()):
            return False, "Door is not adjacent to you"
        if self.door.is_open:
            return False, "Door is already open"
        return True, "Can open"
    
    def execute(self):
        self.door.open()
        self.engine.add_message(EMInfoText("You open "+self.door.reference_noun(specific=True)))
        self.engine.add_message(EMDoorChangedMessage(self.door.id,True))

        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)

class CloseDoorAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,door:GameObject):
        super().__init__("close",actor,engine)
        self.door=door

    def is_possible(self):
        if self.door is None:
            return False, "No door to close."
        if not isinstance(self.door,DoorObject):
            return False, "That is not a door"
        if self.door.get_pos() is None:
            return False, "Door is not on the map"
        #see if door is adjacent to actor
        if self.door not in self.engine.level.map.get_objects_in_cell(self.actor.get_pos()):
            return False, "Door is not adjacent to you"
        if not self.door.is_open:
            return False, "Door is already closed"
        return True, "Can close"
    
    def execute(self):
        self.door.close()
        self.engine.add_message(EMInfoText("You close "+self.door.reference_noun(specific=True)))
        self.engine.add_message(EMDoorChangedMessage(self.door.id,False))
        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)

class OpenContainerAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,container:GameObject):
        super().__init__("open",actor,engine)
        self.container=container

    def is_possible(self):
        if self.container is None:
            return False, "No container to open."
        if not isinstance(self.container,GameObjectContainer):
            return False, "That is not a container"
        if not self.container.closed_not_open:
            return False, "{} is already open".format(self.container.reference_noun(specific=True))
        if self.container.get_pos() is None:
            if self.container not in self.actor.inventory:
                return False, "You don't have {}".format(self.container.reference_noun(specific=True))
        else:
            if self.actor.get_pos().manhattan_distance(self.container.get_pos())>1:
                return False, "{} is too far away.".format(self.container.reference_noun(specific=True))
        return True, "Can open"
    
    def execute(self):
        self.container.action_open(self.actor)
        self.engine.add_message(EMInfoText("You open "+self.container.reference_noun(specific=True)))
        #self.engine.add_message(EMContainerChangedMessage(self.container.id,True))
        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)

class CloseContainerAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,container:GameObject):
        super().__init__("close",actor,engine)
        self.container=container

    def is_possible(self):
        if self.container is None:
            return False, "No container to close."
        if not isinstance(self.container,GameObjectContainer):
            return False, "That is not a container"
        if self.container.closed_not_open:
            return False, "{} is already closed".format(self.container.reference_noun(specific=True))
        if self.container.get_pos() is None:
            if self.container not in self.actor.inventory:
                return False, "You don't have {}".format(self.container.reference_noun(specific=True))
        else:
            if self.actor.get_pos().manhattan_distance(self.container.get_pos())>1:
                return False, "{} is too far away.".format(self.container.reference_noun(specific=True))
        return True, "Can close"
    
    def execute(self):
        self.container.action_close(self.actor)
        self.engine.add_message(EMInfoText("You close "+self.container.reference_noun(specific=True)))
        #self.engine.add_message(EMContainerChangedMessage(self.container.id,True))
        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)

#remove an item from a container
class LootAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,container:GameObject,item:GameObject):
        super().__init__("loot",actor,engine)
        self.container=container
        print("lootaction container is {}".format(container))
        self.item=item

    def is_possible(self):
        if self.container is None:
            return False, "No container to loot."
        if not isinstance(self.container,GameObjectContainer):
            return False, "That is not a container, it's a {}".format(self.container.template_type)
        if self.container.closed_not_open:
            return False, "Container is closed"
        if self.item is None:
            return False, "No item to loot"
        if self.item not in self.container.contents:
            return False, "Item is not in container"
        #if len(self.actor.inventory)>=self.actor.max_inventory:
        #    return False, "Your inventory is full"
        return True, "Can loot"
    
    def execute(self):
        self.container.remove_object(self.item)
        self.actor.inventory.append(self.item)
        self.engine.add_message(EMInfoText("You take "+self.item.reference_noun(specific=True)))
        #self.engine.add_message(EMMapChanged())
        self.engine.add_message(PlayerInventoryChanged())
        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)

#put an item from a container
class InsertAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,container:GameObject,item:GameObject):
        super().__init__("insert",actor,engine)
        self.container=container
        print("lootaction container is {}".format(container))
        self.item=item

    def is_possible(self):
        if self.container is None:
            return False, "No container to insert into."
        if not isinstance(self.container,GameObjectContainer):
            return False, "That is not a container, it's a {}".format(self.container.template_type)
        if self.container.closed_not_open:
            return False, "Container is closed"
        if self.item is None:
            return False, "No item to insert"
        if self.item not in self.actor.inventory:
            return False, "Item is not in your inventory"
        #if len(self.actor.inventory)>=self.actor.max_inventory:
        #    return False, "Your inventory is full"
        return True, "Can insert"
    
    def execute(self):
        self.actor.unequip_item(self.item)
        self.actor.inventory.remove(self.item)        
        self.container.add_object(self.item)

        self.engine.add_message(EMInfoText("You put "+self.item.reference_noun(specific=True)+" in "+self.container.reference_noun(specific=True)))
        #self.engine.add_message(EMMapChanged())
        self.engine.add_message(PlayerInventoryChanged())
        self.engine.level.add_to_entity_initiative(self.actor.id,1.0)