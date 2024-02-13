import pygame
import random
import math
from .GUISprites import get_sprite_store,HashedSpriteArray

class MapAnimation:
    def __init__(self,mapview,engine):
        self.mapview=mapview
        self.engine=engine

    def is_done(self):
        return True
    
    def update(self,clock_time):
        pass

    def draw(self,surf,map_offset):
        ...

    def start(self):
        ...

class MapAnimationMultiple(MapAnimation):
    def __init__(self,mapview,engine,animations):
        super().__init__(mapview,engine)
        self.animations=animations

    def start(self):
        for animation in self.animations:
            animation.start()

    def is_done(self):
        for animation in self.animations:
            if not animation.is_done():
                return False
        return True
    
    def update(self,clock_time):
        for animation in self.animations:
            animation.update(clock_time)

    def draw(self,surf,map_offset):
        for animation in self.animations:
            animation.draw(surf,map_offset)

class MapAnimationMoveObject(MapAnimation):
    def __init__(self,mapview,engine,object_id,start_pos,end_pos,duration):
        super().__init__(mapview,engine)
        self.object_id=object_id
        self.start_pos=start_pos
        self.end_pos=end_pos
        self.duration=duration
        self.on_time=0
        self.done=False

    def start(self):
        self.on_time=0
        self.mapview.object_layer.hide_object(self.object_id)
    
    def is_done(self):
        return self.done
    
    def update(self,clock_time):
        self.on_time+=clock_time
        #print("animation time",self.on_time,self.duration)
        if self.on_time>self.duration:
            self.mapview.object_layer.unhide_object(self.object_id)
            self.done=True

    def draw(self,surf,map_offset):
        object=self.engine.level.object_store.get_object(self.object_id)
        if object is None:
            self.done=True
            self.mapview.object_layer.unhide_object(self.object_id)
            return
        if self.on_time>self.duration:
            self.done=True
            self.mapview.object_layer.unhide_object(self.object_id)
            return
        ppg=self.mapview.pixels_per_grid
        sprite_size=(self.mapview.pixels_per_grid,self.mapview.pixels_per_grid)
        x=self.start_pos.x+(self.end_pos.x-self.start_pos.x)*self.on_time/self.duration
        y=self.start_pos.y+(self.end_pos.y-self.start_pos.y)*self.on_time/self.duration
        #print("animation draw",x,y)
        #print("start",self.start_pos)
        #print("stop",self.end_pos)
        sprite=get_sprite_store().get_sprite_scaled(object.sprite_name,sprite_size)
        surf.blit(sprite,(x*ppg-map_offset[0],y*ppg-map_offset[1]))
        
class MapAnimationShakingSprite(MapAnimation):
    def __init__(self,mapview,engine,cell_pos,sprite_name,duration):
        super().__init__(mapview,engine)
        self.cell_pos=cell_pos
        self.sprite_name=sprite_name
        self.duration=duration
        self.on_time=0
        self.done=False
        self.n_jumps=10
        self.next_jump=duration/self.n_jumps
        self.x_offset=0
        self.y_offset=0

    def start(self):
        self.on_time=0
    
    def is_done(self):
        return self.done

    def update(self,clock_time):
        self.on_time+=clock_time
        if self.on_time>self.duration:
            self.done=True

    def draw(self,surf,map_offset):
        if self.on_time>self.duration:
            self.done=True
            return
        ppg=self.mapview.pixels_per_grid
        if self.on_time>self.next_jump:
            self.next_jump+=self.duration/self.n_jumps
            self.x_offset=random.uniform(-0.3,0.3)
            self.y_offset=random.uniform(-0.3,0.3)
        sprite_size=(self.mapview.pixels_per_grid,self.mapview.pixels_per_grid)
        x=self.cell_pos.x
        y=self.cell_pos.y
        sprite=get_sprite_store().get_sprite_scaled(self.sprite_name,sprite_size)
        surf.blit(sprite,((x+self.x_offset)*ppg-map_offset[0],(y+self.y_offset)*ppg-map_offset[1]))


class MapAnimationMissile(MapAnimation):
    def __init__(self,mapview,engine,sprite_name,start_pos,end_pos,duration):
        super().__init__(mapview,engine)
        self.start_pos=start_pos
        self.end_pos=end_pos
        self.duration=duration
        self.sprite_name=sprite_name
        self.on_time=0
        self.done=False

    def start(self):
        self.on_time=0
        #self.mapview.object_layer.hide_object(self.object_id)
    
    def is_done(self):
        return self.done
    
    def update(self,clock_time):
        self.on_time+=clock_time
        #print("animation time",self.on_time,self.duration)
        if self.on_time>self.duration:
            #print("missile done")
            #self.mapview.object_layer.unhide_object(self.object_id)
            self.done=True

    def draw(self,surf,map_offset):
        ppg=self.mapview.pixels_per_grid
        sprite_size=(self.mapview.pixels_per_grid,self.mapview.pixels_per_grid)
        x=self.start_pos.x+(self.end_pos.x-self.start_pos.x)*self.on_time/self.duration
        y=self.start_pos.y+(self.end_pos.y-self.start_pos.y)*self.on_time/self.duration

        sprite=get_sprite_store().get_sprite_scaled(self.sprite_name,sprite_size)
        #the presumtion is that the missile points straight up as the original sprite
        dx=self.end_pos.x-self.start_pos.x
        dy=self.end_pos.y-self.start_pos.y
        angle=360*math.atan2(-dy,dx)/(2*math.pi)-90
        rotated=pygame.transform.rotate(sprite,angle)


        #TODO Rotate sprite to face direction of travel
        surf.blit(rotated,(x*ppg-map_offset[0],y*ppg-map_offset[1]))

class MapAnimationFlash(MapAnimation):
    def __init__(self,mapview,engine,cell_pos,color,fade_in_duration=50,duration=10,fade_out_duration=50):
        super().__init__(mapview,engine)
        self.cell=cell_pos
        self.color=color
        self.duration=duration
        self.fade_in_duration=fade_in_duration
        self.fade_out_duration=fade_out_duration
        self.duration=duration
        self.durations=[fade_in_duration,duration,fade_out_duration]
        self.on_time=0
        self.done=False

    def start(self):
        self.on_time=0
    
    def is_done(self):
        return self.done
    
    def update(self,clock_time):
        self.on_time+=clock_time
        #print("animation time",self.on_time,self.duration)
        if self.on_time>sum(self.durations):
            #self.mapview.object_layer.unhide_object(self.object_id)
            #print("flash done")
            self.done=True

    def draw(self,surf,map_offset):
        ppg=self.mapview.pixels_per_grid
        if self.on_time<self.durations[0]:
            alpha=self.on_time/self.durations[0]
        elif self.on_time<self.durations[0]+self.durations[1]:
            alpha=1.0
        else:
            alpha=max(1.0-(self.on_time-self.durations[0]-self.durations[1])/self.durations[2],0)
        alphaint=int(255*alpha)
        colora=(self.color[0],self.color[1],self.color[2],alphaint)
        #surf.fill(colora,(self.cell[0]*ppg-map_offset[0],self.cell[1]*ppg-map_offset[1],ppg,ppg),pygame.BLEND_SUB)
        #surf.fill(colora,(self.cell[0]*ppg-map_offset[0],self.cell[1]*ppg-map_offset[1],ppg,ppg),pygame.BLEND_MAX)
        surf.fill(colora,(self.cell[0]*ppg-map_offset[0],self.cell[1]*ppg-map_offset[1],ppg,ppg))

        #surf.fill((0,alphaint,alphaint),(self.cell[0]*ppg-map_offset[0],self.cell[1]*ppg-self.cell[1],ppg,ppg),pygame.BLEND_SUB)
        #surf.fill((alphaint,0,0),(self.cell[0]*ppg-map_offset[0],self.cell[1]*ppg-self.cell[1],ppg,ppg),pygame.BLEND_MAX)

class MapAnimationNudgeObject(MapAnimation):
    def __init__(self,mapview,engine,object_id,start_pos,towards_pos,duration,fraction=0.25):
        super().__init__(mapview,engine)
        self.object_id=object_id
        self.start_pos=start_pos
        self.end_pos=towards_pos
        self.fraction=fraction #fraction of way before turnaround
        self.duration=duration
        self.on_time=0
        self.done=False

    def start(self):
        self.on_time=0
        self.mapview.object_layer.hide_object(self.object_id)
    
    def is_done(self):
        return self.done
    
    def update(self,clock_time):
        self.on_time+=clock_time
        #print("animation time",self.on_time,self.duration)
        if self.on_time>self.duration:
            self.mapview.object_layer.unhide_object(self.object_id)
            self.done=True

    def draw(self,surf,map_offset):
        object=self.engine.level.object_store.get_object(self.object_id)
        if object is None:
            self.done=True
            self.mapview.object_layer.unhide_object(self.object_id)
            return
        if self.on_time>self.duration:
            self.done=True
            self.mapview.object_layer.unhide_object(self.object_id)
            return
        ppg=self.mapview.pixels_per_grid
        sprite_size=(self.mapview.pixels_per_grid,self.mapview.pixels_per_grid)
        if self.on_time<self.duration/2:
            x=self.start_pos.x+self.fraction*(self.end_pos.x-self.start_pos.x)*self.on_time*2/self.duration
            y=self.start_pos.y+self.fraction*(self.end_pos.y-self.start_pos.y)*self.on_time*2/self.duration
        else:
            x=self.start_pos.x+self.fraction*(self.end_pos.x-self.start_pos.x)*(1-self.on_time*2/self.duration)
            y=self.start_pos.y+self.fraction*(self.end_pos.y-self.start_pos.y)*(1-self.on_time*2/self.duration)
        #print("animation draw",x,y)
        #print("start",self.start_pos)
        #print("stop",self.end_pos)
        sprite=get_sprite_store().get_sprite_scaled(object.sprite_name,sprite_size)
        surf.blit(sprite,(x*ppg-map_offset[0],y*ppg-map_offset[1]))