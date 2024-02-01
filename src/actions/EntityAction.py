from ..game_engine.GameEngine import GameEngine
from ..game_engine.EngineMessage import *
from ..level.GameObject import GameObject
from ..level.Entity import Entity
from ..level.MapCoord import Direction,MapCoord


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
        level.map.remove_object_from_cell(self.actor,self.actor.get_pos())
        level.map.add_object_to_cell(self.actor,new_pos)
        self.engine.add_message(EMObjectMoved(self.actor.id,old_pos,new_pos))

    def is_possible(self):
        level=self.actor.get_level()
        if self.actor.get_pos() is None:
            return False, "Actor has no location"
        if not level.map.is_passable(self.actor.get_pos(),self.direction):
            return False, "You cannot go that way"
        new_pos=self.actor.get_pos()+MapCoord.direction_to_vector(self.direction)
        for object in level.map.get_objects_in_cell(new_pos):
            if object.block_movement:
                return False, "There is something in your way"
            else:
                print("There is a {} not in the way".format(object.reference_noun(specific=False)))
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
        self.engine.add_message(EMMapChanged())
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
        self.engine.add_message(EMInfoText("You unequip "+self.object.reference_noun(specific=True)))
        #self.engine.add_message(EMMapChanged())
        self.engine.add_message(PlayerInventoryChanged())

#Melee attack
class MeleeAction(EntityAction):
    def __init__(self,actor:Entity,engine:GameEngine,target:Entity):
        super().__init__("melee_attack",actor,engine)
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
        damage=weapon.melee_info["damage"]
        text=weapon.melee_info["your_text"]
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
        super().__init__("melee_attack",actor,engine)
        self.target=target

    def is_possible(self):
        if self.target is None:
            return False, "No target to attack"
        weapon=self.actor.get_missile_weapon()

        if weapon is None:
            return False, "You have no missile weapon"
        if weapon.ranged_info is None:
            return False, "Your missile weapon cannot be used for ranged attacks"
        #TODO ammo
        range=weapon.ranged_info["range"]
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
        damage=weapon.ranged_info["damage"]
        text=weapon.ranged_info["your_text"]
        range=weapon.ranged_info["range"]
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