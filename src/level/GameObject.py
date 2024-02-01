import yaml
import uuid
import copy
from .MapCoord import MapCoord,Direction

gameobject_constructors={}
def register_gameobject_constructor(name,constructor):
    gameobject_constructors[name]=constructor


class GameObject:
    def __init__(self,**kwparams):
        
        self.template_type=None
        self.game_engine=kwparams.get("game_engine",None)
        self.object_store=kwparams.get("object_store",None)
        object=kwparams.get("object",{})
        self.id=object.get("id",uuid.uuid4())
        self.pos=MapCoord(object.get("pos",(0,0)))
        self.noun=object.get("reference","thing")
        self.sprite_name=object.get("sprite_name","")
        self.block_movement=object.get("block_movement",False)
        self.in_level=object.get("in_level",None)
        self.contained_by=None
        self.is_takable=object.get("is_takable",True)
        #recarding equipment
        self.equip_slot=object.get("equip_slot",None) #could be left_hand,right_hand, head, etc

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

    def get_pos(self):
        return self.pos
    
    def get_level(self):
        return self.in_level
    
    def set_level(self,level):
        self.in_level=level
    
    def populate_subobjects(self):
        ...

    def set_location(self,pos):
        #pos is a tuple (x,y)
        self.pos=pos

    def __str__(self):
        return "{} named {}".format(self.template_type,self.reference_noun())
gameobject_constructors["GameObject"]=GameObject



class Weapon(GameObject):
    def __init__(self,**kwparams):
        super().__init__(**kwparams)
        object=kwparams.get("object",{})
        if "melee_attack" in object:
            self.melee_info=object["melee_attack"]
        else:
            self.melee_info=None
        if "ranged_attack" in object:
            self.ranged_info=object["ranged_attack"]
        else:
            self.ranged_info=None
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
