from .GameObject import GameObject,register_gameobject_constructor
from .GraphPaperMap import CellType, string_to_celltype
from ..level.ObjectFactory import create_object_from_template

class Entity(GameObject):
    def __init__(self,**kwparams):
        super().__init__(**kwparams)
        object=kwparams.get("object",{})
        self.dead=False #set to true when it can no longer act
        self.initiative=0
        self.max_hp=object.get("max_hp",4)
        self.hp=object.get("hp",self.max_hp)
        self.inventory=[] #these are object ids
        self.block_movement=object.get("block_movement",True)
        self.behavior=None
        self.equip_slots=["head","main_hand","off_hand","body","missile"]
        self.equipment={} #these are item ids
        for slot in self.equip_slots:
            self.equipment[slot]=None
        self.default_weapon_type=object.get("default_weapon",None)
        #vision
        self.vision=object.get("vision",6) #in squares, illuminated >128
        self.dark_vision=object.get("dark_vision",2) #in squares, illuminated <128

        #mobility
        passable_cell_string=object.get("passable_cells",["outdoor_grass","indoor_floor","indoor_clean_floor"])
        self.passable_cells=[string_to_celltype(x) for x in passable_cell_string]
        #print("passable cells",self.passable_cells)
        #overrides
        self.is_takable=False


    def get_melee_weapon(self):
        if self.equipment["main_hand"] is not None:
            return self.equipment["main_hand"]
        if self.default_weapon_type is not None:
            return create_object_from_template(self.default_weapon_type)
        return None
    
    def get_missile_weapon(self):
        if self.equipment["missile"] is not None:
            return self.equipment["missile"]
        if self.default_weapon_type is not None:
            return create_object_from_template(self.default_weapon_type)
        return None

    def get_equipped_item(self,slot):
        if slot in self.equipment:
            return self.equipment[slot]
        else:
            return None
        
    def get_equipped_slot(self,item): #if item is equipped, say which slot it is in
        for slot in self.equip_slots:
            if self.equipment[slot]==item:
                return slot
        return None

    def equip_item(self,item):
        #walk through the list of slots and equip the item to the first available slot
        slot=item.equip_slot
        if self.get_equipped_item(slot) is not None:
            self.unequip_slot(slot)
        self.equipment[slot]=item
        return True
    
    def unequip_item(self,item):
        for slot in self.equip_slots:
            if self.equipment[slot]==item:
                self.equipment[slot]=None
                return True
        return False
    
    def unequip_slot(self,slot):
        self.equipment[slot]=None
        return True
    
    def get_visible_cells(self,map): #returns a list of visible cells
        possibly_visible,nearby=map.get_visible_cells(self.get_pos(),self.vision)
        visible=[]
        for cell in possibly_visible:
            if map.get_cell(cell).light_level>128:
                visible.append(cell)
            elif self.get_pos().manhattan_distance(cell)<self.dark_vision:
                #print("visible but dark")
                visible.append(cell)
        #TODO adjust nearby to remove cells that are not visible
        return visible
    
    #for lighting
    def get_lighting_params(self):
        max_radius=self.light_radius
        max_intensity=self.light_intensity
        for item in self.equipment.values():
            if item is not None:
                radius,intensity=item.get_lighting_params()
                if radius>max_radius:
                    max_radius=radius
                if intensity>max_intensity:
                    max_intensity=intensity
        #if self.game_engine is None:
        #    print("object {} has no ref to game enine".format(self.reference_noun()))
        #if self.id==self.game_engine.get_player_id():
        #if self.noun=="player":
        #    print("returning light params",max_radius,max_intensity)
        return max_radius,max_intensity
        
register_gameobject_constructor("Entity",Entity)
