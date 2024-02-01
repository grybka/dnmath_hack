import pygame
import yaml

class GUISpriteStore:
    def __init__(self):
        ...
        self.sprite_info_loaded=False
        self.sprites={} #these are the base sprites
        self.scaled_sprites={} #these are sprites scaled to a certain size
        self.loaded_sheets={} #these are sheets from which one can pull sprites

    def get_sprite(self,sprite_name):
        #print("get sprite: "+sprite_name)
        if not self.sprite_info_loaded:
            self.load_sprite_info()
            self.sprite_info_loaded=True
        if sprite_name not in self.sprites:
            #try:
            self.load_sprite(sprite_name,self.sprite_info_file[sprite_name])
            #except:
            #    return self.sprites["unknown"]
        return self.sprites[sprite_name]
    
    def get_sprite_scaled(self,sprite_name,size):
        key=(sprite_name,size)
        if key not in self.scaled_sprites:
            sprite=self.get_sprite(sprite_name)
            self.scaled_sprites[key]=pygame.transform.scale(sprite,size)
        return self.scaled_sprites[key]

    #loading functios below    
    def get_or_load_sheet(self,sheet_fname):
        #return it if I've already loaded it
        if sheet_fname in self.loaded_sheets:
            return self.loaded_sheets[sheet_fname]
        #otherwise load it
        sheet=pygame.image.load(sheet_fname)
        self.loaded_sheets[sheet_fname]=sheet
        return sheet

    def load_sprite(self,sprite_name,info_object):
        fname=info_object["file"]
        sheet=self.get_or_load_sheet(fname)
        rect=(0,0,sheet.get_width(),sheet.get_height() )
        if "rect" in info_object:
            rect = info_object["rect"]
        #my_surf=pygame.Surface((rect[2],rect[3]))
        #if "background_color" in info_object:
        #    my_surf.fill(info_object["background_color"])
        my_surf=sheet.subsurface(rect)
        #my_surf.blit(sheet,(0,0),rect)
        if "transforms" in info_object:
            for transform in info_object["transforms"]:
                if transform=="hflip":
                    my_surf=pygame.transform.flip(my_surf,True,False)
                elif transform=="vflip":
                    my_surf=pygame.transform.flip(my_surf,False,True)
                elif transform=="r_rotate":
                    my_surf=pygame.transform.rotate(my_surf,90)
                else:
                    raise Exception("Unknown transform: "+transform)
        self.sprites[sprite_name]=my_surf

    def load_sprite_info(self,info_fname="data/graphics/sprite_info.yaml"):
        with open(info_fname, 'r') as file:
            self.sprite_info_file = yaml.safe_load(file)
        #special sprites
        blank_sprite=pygame.Surface((256,256))
        blank_sprite.fill((255,255,255))
        self.sprites["blank"]=blank_sprite
        clear_sprite=pygame.Surface((256,256))
        clear_sprite.set_colorkey((0,0,0))
        self.sprites["clear"]=clear_sprite

    def load_all_sprites(self,info_fname="data/sprite_info.yaml"):
        self.load_sprite_info(info_fname)
        for sprite_name,sprite_info in self.sprite_info_file.items():
            self.load_sprite(sprite_name,sprite_info)

_sprite_store=GUISpriteStore()

def get_sprite_store():
    return _sprite_store

#Some types of cells have multiple pictures that should be chosen randomly
#This class helps with that
class HashedSpriteArray:
    def __init__(self):
        self.sprites=[]
        self.frequencies=[]

    def add_sprite_name(self,name,frequency):
        self.sprites.append(name)
        self.frequencies.append(frequency)

    def choose_sprite(self,hashable):
        choice=hash(hashable)%sum(self.frequencies)
        #choice=random.randint(0,sum(self.frequencies)-1)
        for i in range(len(self.frequencies)):
            choice-=self.frequencies[i]
            if choice<0:
                return self.sprites[i]