import yaml
import uuid
import copy
from .MapCoord import MapCoord,Direction
from enum import Enum
from ..language.producer import ProductionGrammar,Production,Symbol

gameobject_constructors={}
def register_gameobject_constructor(name,constructor):
    gameobject_constructors[name]=constructor


class GameObject:
    def __init__(self,**kwparams):
        
        self.template_type=None
        #self.game_engine=kwparams.get("game_engine",None)
        self.object_store=kwparams.get("object_store",None)
        object=kwparams.get("object",{})
        self.id=object.get("id",uuid.uuid4())
        self.pos=MapCoord(object.get("pos",(0,0)))
        self.noun=object.get("reference","thing")
        self.sprite_name=object.get("sprite_name",None)
        self.block_movement=object.get("block_movement",False)
        self.in_level=object.get("in_level",None)
        self.contained_by=None
        self.is_takable=object.get("is_takable",True)
        self.read_message=object.get("read_message",None)
        #recarding equipment
        self.equip_slot=object.get("equip_slot",None) #could be left_hand,right_hand, head, etc
        #light
        self.light_radius=object.get("light_radius",0)
        self.light_intensity=object.get("light_intensity",0)
        self.lighting_cells=None
        self.needs_light_update=False

    def reference_noun(self,specific=False):
        if specific:
            return "the {}".format(self.noun)
        else:
            if self.noun[0] in "aeiou":
                return "an {}".format(self.noun)
            else:
                return "a {}".format(self.noun)
            
    def set_pos(self,pos):
        self.pos=pos
        self.was_moved()

    def get_pos(self):
        return self.pos
    
    def get_level(self):
        return self.in_level
    
    def set_level(self,level):
        self.in_level=level
    
    def populate_subobjects(self):
        ...

    #use this instead of sprite_name directly in case an object changes how it looks
    def get_sprite_name(self):
        return self.sprite_name

    #call this every time the object is moved
    def was_moved(self):
        if self.get_lighting_params()[0]>0:
            self.needs_light_update=True

    #for lighting
    def get_lighting_params(self):
        return self.light_radius,self.light_intensity


    def __str__(self):
        return "{} named {}".format(self.template_type,self.reference_noun())
gameobject_constructors["GameObject"]=GameObject

class GameObjectContainer(GameObject):
    def __init__(self,**kwparams):
        super().__init__(**kwparams)
        object=kwparams.get("object",{})

        self.closed_not_open=object.get("closed_not_open",True)
        self.open_sprite_name=object.get("open_sprite_name",None)
        self.closed_sprite_name=object.get("closed_sprite_name",None)
        self.contents=[]
        self.max_contents=object.get("max_contents",10)

    def get_sprite_name(self):
        ret=None
        if self.closed_not_open:
            ret= self.closed_sprite_name
        else:
            ret= self.open_sprite_name
        return ret
    
    def action_open(self,opener):
        if self.closed_not_open:
            self.closed_not_open=False
            self.was_moved()
            return True
        return False
    
    def action_close(self,closer):
        if not self.closed_not_open:
            self.closed_not_open=True
            self.was_moved()
            return True
        return False
    
    def add_object(self,obj):
        if len(self.contents)<self.max_contents:
            self.contents.append(obj)
            obj.contained_by=self
            obj.was_moved()
            return True
        return False
    
    def remove_object(self,obj):
        if obj in self.contents:
            self.contents.remove(obj)
            obj.contained_by=None
            obj.was_moved()
            return True
        return False
    
gameobject_constructors["Container"]=GameObjectContainer


class AttackType(Enum):
    MELEE = 0
    RANGED = 1

class AttackInfo:
    def __init__(self,**kwparams):
        self.attack_type=AttackType[kwparams.get("attack_type","MELEE").upper()]
        self.damage=kwparams.get("damage",1)
        self.range=kwparams.get("range",1)
        self.your_attack_text=kwparams.get("your_text","You attack")
        self.enemy_attack_text=kwparams.get("enemy_text","It attacks")
        self.message_producer=ProductionGrammar()
        self.message_producer.add_production(Production("your_attack_text -> \""+self.your_attack_text+"\""))
        self.message_producer.add_production(Production("enemy_attack_text -> \""+self.enemy_attack_text+"\""))

    def is_ranged(self):
        return self.attack_type==AttackType.RANGED
    
    def is_melee(self):
        return self.attack_type==AttackType.MELEE

    def get_your_attack_message(self,attacker,defender):
        return self.your_attack_text

    def get_enemy_attack_message(self,attacker,defender):
        return self.enemy_attack_text

class Weapon(GameObject):
    def __init__(self,**kwparams):
        super().__init__(**kwparams)
        object=kwparams.get("object",{})
        if "attack_info" in object:
            self.attack_info=AttackInfo(**object["attack_info"])
gameobject_constructors["Weapon"]=Weapon

class Portal(GameObject):
    def __init__(self,**kwparams):
        super().__init__(**kwparams)
        object=kwparams.get("object",{})
        self.destination=object.get("destination",None)
        self.destination_pos=object.get("destination_pos",None)
        self.destination_map=object.get("destination_map",None)
        self.is_takable=False
gameobject_constructors["Portal"]=Portal
