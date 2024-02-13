import pygame
import yaml
from ..gui_core.GUIElement import GUIElement, point_in_rect
from .GUISprites import get_sprite_store,HashedSpriteArray
from ..level.MapCoord import MapCoord
from ..level.GraphPaperMap import string_to_celltype,WallType,MapMask,CellVisibility,CellType
from .Animations import MapAnimationMoveObject
from .GUIEvents import *
from .beziercurve import hand_sketch_line
from ..level.Entity import Entity

#layers:
#background
#cells
#walls
#objects
#animations
#visibility
#selection overlay

class MVLayer:
    def __init__(self,engine,mapview):
        self.engine=engine
        self.mapview=mapview
        self.needs_rerender=True

    def suggest_rerender(self):
        self.needs_rerender=True

    def new_map(self):
        ...

class MVCellLayer(MVLayer):
    def __init__(self,engine,mapview):
        super().__init__(engine,mapview)
        self.rendered_surf=None
        self.cell_sprites={}
        #self.cell_colors={}
        #self.cell_colors[CellType.OUTDOOR_GRASS]=(200,255,200)
        #self.cell_colors[CellType.IMPASSIBLE]=(200,200,200)
        #self.cell_colors[CellType.EXIT]=(200,255,200)
        #self.cell_colors[CellType.INDOOR_FLOOR]=(181,101,29)
        #self.cell_colors[CellType.INDOOR_CLEAN_FLOOR]=(181,101,29)

        #invert cell colors
        #for cell_type in self.cell_colors:
        #    self.cell_colors[cell_type]=(255-self.cell_colors[cell_type][0],255-self.cell_colors[cell_type][1],255-self.cell_colors[cell_type][2])

    def render(self,offset): #rebuild internal surface
        pixels_per_grid=self.mapview.pixels_per_grid
        if self.rendered_surf==None:
            self.rendered_surf=pygame.Surface((self.engine.level.map.width*pixels_per_grid,self.engine.level.map.height*pixels_per_grid))
        self.rendered_surf.fill((0,0,0,0))
        for x in range(self.engine.level.map.width):
            for y in range(self.engine.level.map.height):
                cell=self.engine.level.map.get_cell(MapCoord(x,y))
                if cell.cell_type in self.cell_sprites:
                    sprite_name=self.cell_sprites[cell.cell_type].choose_sprite(cell.random_number)
                    sprite=get_sprite_store().get_sprite_scaled(sprite_name,(pixels_per_grid,pixels_per_grid))
                    self.rendered_surf.blit(sprite,(x*pixels_per_grid,y*pixels_per_grid))
                    #if cell.cell_type in self.cell_colors:
                    #    self.rendered_surf.fill(self.cell_colors[cell.cell_type],(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid),pygame.BLEND_RGB_SUB)
                else:
                    #draw a red square for missing sprite
                    self.rendered_surf.fill((255,0,0),(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid))
        #draw graph paper grid
        graph_line_color=(235,235,255)
        for x in range(self.engine.level.map.width):
            pygame.draw.line(self.rendered_surf,graph_line_color,(x*pixels_per_grid,0),(x*pixels_per_grid,self.engine.level.map.height*pixels_per_grid))
        for y in range(self.engine.level.map.height):
            pygame.draw.line(self.rendered_surf,graph_line_color,(0,y*pixels_per_grid),(self.engine.level.map.width*pixels_per_grid,y*pixels_per_grid))

    def draw(self,surf,map_offset): #map offset is the offset of the map in pixels
        if self.needs_rerender or self.rendered_surf is None:
            self.render(map_offset)
            self.needs_rerender=False
        surf.blit(self.rendered_surf,(-map_offset[0],-map_offset[1]))

    def new_map(self):
        self.needs_rerender=True
        self.rendered_surf=None
        self.cell_sprites=self.mapview.tilesets[self.engine.level.tileset_name]

#cells in view with good lighting get color
class MVCellColorLayer(MVLayer):
    def __init__(self,engine,mapview):
        super().__init__(engine,mapview)
        self.cell_colors={}
        self.colorsets={}
        self.load_cell_colors()
        self.rendered_surf=None

    def load_cell_colors(self,fname="data/graphics/map_colorsets.yaml"):
        with open(fname,"r") as f:
            self.colorsets=yaml.safe_load(f)

    def draw(self,surf,map_offset):
        if self.needs_rerender or self.rendered_surf is None:
            self.render()
            self.needs_rerender=False
        surf.blit(self.rendered_surf,(-map_offset[0],-map_offset[1]))

    def new_map(self):
        self.rendered_surf=None
        self.needs_rerender=True
        if self.engine.level.tileset_name in self.colorsets:
            print("loading colorset for {}".format(self.engine.level.tileset_name))
            for key in self.colorsets[self.engine.level.tileset_name]:
                color=self.colorsets[self.engine.level.tileset_name][key]
                self.cell_colors[string_to_celltype(key)]=( color[0],color[1],color[2],150)
                #self.cell_colors[string_to_celltype(key)]=( 255-color[0],255-color[1],255-color[2])
    
    def render(self):
        #print("rendering visibility")
        pixels_per_grid=self.mapview.pixels_per_grid
        if self.rendered_surf==None:
            self.rendered_surf=pygame.Surface((self.engine.level.map.width*pixels_per_grid,self.engine.level.map.height*pixels_per_grid),pygame.SRCALPHA)
        visibility=self.engine.level.memory_mask
        #this is probably not the best place to do it, but
        #I have to recalculate the player's visibility sometime
        map=self.engine.level.map
        #self.engine.level.map.update_map_mask(visibility,self.engine.get_player().get_pos(),distance=5)
        lowest_level=180
        def light_level_to_color(light_level):
            return (0,0,0,max(min(255-light_level,lowest_level),0))
        remembered_shading=(0,0,0,lowest_level)
        hidden_shading=(0,0,0,255)
        for x in range(self.engine.level.map.width):
            for y in range(self.engine.level.map.height):
                if visibility.cells[x][y]==CellVisibility.VISIBLE:
                    shading=light_level_to_color(map.get_cell(MapCoord(x,y)).light_level)
                    #print("shading is ",shading)
                    if map.get_cell(MapCoord(x,y)).cell_type in self.cell_colors:
                        shading=self.cell_colors[map.get_cell(MapCoord(x,y)).cell_type]
                        self.rendered_surf.fill(shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid))
                        #self.rendered_surf.fill(shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid),pygame.BLEND_RGB_SUB)
                    self.rendered_surf.fill(shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid))
                elif visibility.cells[x][y]==CellVisibility.REMEMBERED:
                    self.rendered_surf.fill(remembered_shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid))
                else:
                    self.rendered_surf.fill(hidden_shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid))
    


class MVWallLayer(MVLayer):
    def __init__(self,engine,mapview):
        super().__init__(engine,mapview)
        self.rendered_surf=None


    def render(self,offset): #rebuild internal surface
        pixels_per_grid=self.mapview.pixels_per_grid
        if self.rendered_surf==None:
            self.rendered_surf=pygame.Surface((self.engine.level.map.width*pixels_per_grid,self.engine.level.map.height*pixels_per_grid),pygame.SRCALPHA)
        print("rerendireing walls")
        self.rendered_surf.fill((0,0,0,0))
        for x in range(self.engine.level.map.width):
            for y in range(self.engine.level.map.height):
                cell=self.engine.level.map.get_cell(MapCoord(x,y))
                self.render_wall(cell.walls[0].wall_type,(x*pixels_per_grid,y*pixels_per_grid),((x+1)*pixels_per_grid,y*pixels_per_grid),cell.walls[0].random_number)
                self.render_wall(cell.walls[1].wall_type,((x+1)*pixels_per_grid,y*pixels_per_grid),((x+1)*pixels_per_grid,(y+1)*pixels_per_grid),cell.walls[1].random_number)
                self.render_wall(cell.walls[2].wall_type,((x+1)*pixels_per_grid,(y+1)*pixels_per_grid),(x*pixels_per_grid,(y+1)*pixels_per_grid),cell.walls[2].random_number)
                self.render_wall(cell.walls[3].wall_type,(x*pixels_per_grid,(y+1)*pixels_per_grid),(x*pixels_per_grid,y*pixels_per_grid),cell.walls[3].random_number)

    def render_wall(self,wall_type,from_pixel,to_pixel,random_seed=None):
        door_wall_fraction=0.1 #fraction of length
        door_thickness=0.1 #fraction of length
        if wall_type==WallType.WALL:
            #pygame.draw.line(self.rendered_surf,(0,0,0,255),from_pixel,to_pixel,5)
            hand_sketch_line(self.rendered_surf,from_pixel,to_pixel,(0,0,0,255),5,random_seed=random_seed)
        elif wall_type==WallType.DOOR_CLOSED:
            thick_px=int(door_thickness*self.mapview.pixels_per_grid)
            pt1=from_pixel
            pt2=( int(from_pixel[0]+door_wall_fraction*(to_pixel[0]-from_pixel[0])),int(from_pixel[1]+door_wall_fraction*(to_pixel[1]-from_pixel[1])))
            pt3=( int(to_pixel[0]-door_wall_fraction*(to_pixel[0]-from_pixel[0])),int(to_pixel[1]-door_wall_fraction*(to_pixel[1]-from_pixel[1])))
            pt4=to_pixel
            pygame.draw.line(self.rendered_surf,(0,0,0,255),pt1,pt2,5)
            pygame.draw.line(self.rendered_surf,(0,0,0,255),pt3,pt4,5)
            if pt1[0]==pt2[0]:
                pygame.draw.rect(self.rendered_surf,(255,255,255,255),(pt2[0]-thick_px,pt2[1],2*thick_px,pt3[1]-pt2[1]))    
                pygame.draw.rect(self.rendered_surf,(0,0,0,255),(pt2[0]-thick_px,pt2[1],2*thick_px,pt3[1]-pt2[1]),3)    
            else:
                pygame.draw.rect(self.rendered_surf,(255,255,255,255),(pt2[0],pt2[1]-thick_px,pt3[0]-pt2[0],2*thick_px))
                pygame.draw.rect(self.rendered_surf,(0,0,0,255),(pt2[0],pt2[1]-thick_px,pt3[0]-pt2[0],2*thick_px),3)
        elif wall_type==WallType.DOOR_OPEN:
            thick_px=int(door_thickness*self.mapview.pixels_per_grid)
            pt1=from_pixel
            pt2=( int(from_pixel[0]+door_wall_fraction*(to_pixel[0]-from_pixel[0])),int(from_pixel[1]+door_wall_fraction*(to_pixel[1]-from_pixel[1])))
            pt3=( int(to_pixel[0]-door_wall_fraction*(to_pixel[0]-from_pixel[0])),int(to_pixel[1]-door_wall_fraction*(to_pixel[1]-from_pixel[1])))
            pt4=to_pixel
            pygame.draw.line(self.rendered_surf,(0,0,0,255),pt1,pt2,5)
            pygame.draw.line(self.rendered_surf,(0,0,0,255),pt3,pt4,5)
            if pt1[0]==pt2[0]:
                #pygame.draw.rect(self.rendered_surf,(255,255,255,255),(pt2[0]-thick_px,pt2[1],2*thick_px,pt3[1]-pt2[1]))    
                pygame.draw.rect(self.rendered_surf,(0,0,0,255),(pt2[0]-thick_px,pt2[1],2*thick_px,thick_px),3)    
            else:
                #pygame.draw.rect(self.rendered_surf,(255,255,255,255),(pt2[0],pt2[1]-thick_px,pt3[0]-pt2[0],2*thick_px))
                pygame.draw.rect(self.rendered_surf,(0,0,0,255),(pt2[0],pt2[1]-thick_px,thick_px,2*thick_px),3)
            ...

    def draw(self,surf,map_offset):
        if self.needs_rerender:
            self.render(map_offset)
            self.needs_rerender=False
        surf.blit(self.rendered_surf,(-map_offset[0],-map_offset[1]))

    def new_map(self):
        self.needs_rerender=True
        self.rendered_surf=None

class MVObjectLayer(MVLayer):
    def __init__(self,engine,mapview):
        super().__init__(engine,mapview)
        self.hidden_object_ids=[]
        

    def draw(self,surf,map_offset):
        #I don't think it will help to pre-render
        min_x,min_y,max_x,max_y=self.mapview.get_tiles_in_view()
        sprite_size=(self.mapview.pixels_per_grid,self.mapview.pixels_per_grid)
        visibility=self.engine.level.memory_mask
        #print("drawing objects in view",min_x,min_y,max_x,max_y)
        for i in range(min_x,max_x):
            for j in range(min_y,max_y):
                cell=MapCoord(i,j)
                #TODO figure out draw order 
                if visibility.cells[i][j]==CellVisibility.VISIBLE:
                    for obj in self.engine.level.map.get_objects_in_cell(cell):
                        if obj.id in self.hidden_object_ids:
                            continue
                        if obj.get_sprite_name() is None:
                            continue
                        #print("drawing object at {}",obj.sprite_name,cell)
                        sprite=get_sprite_store().get_sprite_scaled(obj.get_sprite_name(),sprite_size)
                        surf.blit(sprite,(i*self.mapview.pixels_per_grid-map_offset[0],j*self.mapview.pixels_per_grid-map_offset[1]))
                        if isinstance(obj,Entity):
                            if obj.hp<obj.max_hp:
                                self.draw_health_bar(surf,(i*self.mapview.pixels_per_grid-map_offset[0],j*self.mapview.pixels_per_grid-map_offset[1]),self.mapview.pixels_per_grid,obj.hp,obj.max_hp)


    def draw_health_bar(self,surf,sprite_pos,ppg,health,max_health):
        #draw health bar
        health_bar_height=5
        health_bar_border=1
        #10 percent down from top
        #80 percent wide
        health_bar_x=int(sprite_pos[0]+0.1*ppg)
        health_bar_y=int(sprite_pos[1]+0.1*ppg)
        health_bar_width=int(ppg*0.8)

        health_bar_color_border=(100,100,100)
        health_bar_color=(0,255,0)
        health_bar_bg_color=(0,0,0)
        health_bar_length=health_bar_width*health/max_health
        pygame.draw.rect(surf,health_bar_color_border,(health_bar_x-health_bar_border,health_bar_y-health_bar_border,health_bar_width+2*health_bar_border,health_bar_height+2*health_bar_border))
        pygame.draw.rect(surf,health_bar_bg_color,(health_bar_x,health_bar_y,health_bar_width,health_bar_height))
        pygame.draw.rect(surf,health_bar_color,(health_bar_x,health_bar_y,health_bar_length,health_bar_height))

    def hide_object(self,object_id):
        self.hidden_object_ids.append(object_id)

    def unhide_object(self,object_id):
        self.hidden_object_ids=[obj_id for obj_id in self.hidden_object_ids if obj_id!=object_id]

    def new_map(self):
        self.needs_redraw=True

class MVVisibilityLayer(MVLayer):
    def __init__(self,engine,mapview):
        super().__init__(engine,mapview)
#        self.visibility=MapMask(self.engine.level.map.width,self.engine.level.map.height)
        self.rendered_surf=None
        self.needs_rerender=True

        self.cell_colors={}
        self.colorsets={}
        self.load_cell_colors()

    def load_cell_colors(self,fname="data/graphics/map_colorsets.yaml"):
        with open(fname,"r") as f:
            self.colorsets=yaml.safe_load(f)

    def draw(self,surf,map_offset):
        if self.needs_rerender or self.rendered_surf is None:
            self.render()
            self.needs_rerender=False
        surf.blit(self.rendered_surf,(-map_offset[0],-map_offset[1]))

    def new_map(self):
        self.rendered_surf=None
        self.needs_rerender=True
        if self.engine.level.tileset_name in self.colorsets:
            print("loading colorset for {}".format(self.engine.level.tileset_name))
            for key in self.colorsets[self.engine.level.tileset_name]:
                color=self.colorsets[self.engine.level.tileset_name][key]
                self.cell_colors[string_to_celltype(key)]=( color[0],color[1],color[2],150)
                #self.cell_colors[string_to_celltype(key)]=( 255-color[0],255-color[1],255-color[2])
        
    def render(self):
        #print("rendering visibility")
        pixels_per_grid=self.mapview.pixels_per_grid
        if self.rendered_surf==None:
            self.rendered_surf=pygame.Surface((self.engine.level.map.width*pixels_per_grid,self.engine.level.map.height*pixels_per_grid),pygame.SRCALPHA)
        visibility=self.engine.level.memory_mask
        #this is probably not the best place to do it, but
        #I have to recalculate the player's visibility sometime
        map=self.engine.level.map
        #self.engine.level.map.update_map_mask(visibility,self.engine.get_player().get_pos(),distance=5)
        lowest_level=180
        def light_level_to_color(light_level):
            return (0,0,0,max(min(255-light_level,lowest_level),0))
        remembered_shading=(0,0,0,lowest_level)
        hidden_shading=(0,0,0,255)
        for x in range(self.engine.level.map.width):
            for y in range(self.engine.level.map.height):
                if visibility.cells[x][y]==CellVisibility.VISIBLE:
                    shading=light_level_to_color(map.get_cell(MapCoord(x,y)).light_level)
                    #print("shading is ",shading)
                    if map.get_cell(MapCoord(x,y)).cell_type in self.cell_colors:
                        shading=self.cell_colors[map.get_cell(MapCoord(x,y)).cell_type]
                        self.rendered_surf.fill(shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid))
                        #self.rendered_surf.fill(shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid),pygame.BLEND_RGB_SUB)
                    self.rendered_surf.fill(shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid))
                elif visibility.cells[x][y]==CellVisibility.REMEMBERED:
                    self.rendered_surf.fill(remembered_shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid))
                else:
                    self.rendered_surf.fill(hidden_shading,(x*pixels_per_grid,y*pixels_per_grid,pixels_per_grid,pixels_per_grid))
    

class MVAnimationLayer(MVLayer):
    def __init__(self,engine,mapview):
        super().__init__(engine,mapview)
        self.animations=[]

    def draw(self,surf,map_offset):
        for animation in self.animations:
            animation.draw(surf,map_offset)

    def new_map(self):
        ...

    def update(self,clock_time):
        for animation in self.animations:
            animation.update(clock_time)
        self.animations=[animation for animation in self.animations if not animation.is_done()]

class MVSelectionLayer(MVLayer):
    def __init__(self,engine,mapview):
        super().__init__(engine,mapview)
        self.selected_cell=None

    def draw(self,surf,map_offset):
        if self.selected_cell is None:
            return
        selected_color=(255,0,0)
        pygame.draw.rect(surf,selected_color,(self.selected_cell.x*self.mapview.pixels_per_grid-map_offset[0],self.selected_cell.y*self.mapview.pixels_per_grid-map_offset[1],self.mapview.pixels_per_grid,self.mapview.pixels_per_grid),2)

    def new_map(self):
        ...

    

    def set_selected_cell(self,cell):
        self.selected_cell=cell

class GUIMapView(GUIElement):
    def __init__(self,engine):
        super().__init__()
        self.grids_per_screen=10
        self.engine=engine
        self.map_offset=(0,0) #offset of the map in pixels
        self.pixels_per_grid=100 #updated with resize
        #tracking
        self.elasticity=0.05
        self.maxvel=7
        self.tracking_slop_grids_x=2
        self.tracking_slop_grids_y=1
        self.turbo_tracking=False
        #tilesets
        self.tilesets={}
        self.load_tilesets("data/graphics/map_tilesets.yaml")
        self.layers=[]
        self.cell_layer=MVCellLayer(engine,self)
        self.layers.append(self.cell_layer)
        self.cell_color_layer=MVCellColorLayer(engine,self)
        self.layers.append(self.cell_color_layer)
        self.wall_layer=MVWallLayer(engine,self)
        self.layers.append(self.wall_layer)
        self.visibility_layer=MVVisibilityLayer(engine,self)
        #self.layers.append(self.visibility_layer)
        self.object_layer=MVObjectLayer(engine,self)
        self.layers.append(self.object_layer)
        self.animation_layer=MVAnimationLayer(engine,self)
        self.layers.append(self.animation_layer)
        self.selection_layer=MVSelectionLayer(engine,self)
        self.layers.append(self.selection_layer)
        self.new_map()
        

    def handle_event(self,event,window_offset=(0,0)):
        if event.type==pygame.MOUSEBUTTONDOWN:
            if point_in_rect( (event.pos[0]-window_offset[0],event.pos[1]-window_offset[1]),self.rect):
                if event.button==1:
                    cell=self.pixel_to_cell((event.pos[0]-window_offset[0],event.pos[1]-window_offset[1]))
                    self.selection_layer.set_selected_cell(cell)
                    pygame.event.post(pygame.event.Event(CELL_SELECTED_EVENT,{"cell": cell}))
                    return True
                elif event.button==3:
                    cell=self.pixel_to_cell((event.pos[0]-window_offset[0],event.pos[1]-window_offset[1]))
                    pygame.event.post(pygame.event.Event(CELL_RIGHTCLICKED_EVENT,{"cell": cell}))
                    return True
                else:
                    print("button was not 1, it was {}".format(event.button))
        return False

    def update(self,clock_time):
        if self.engine is not None:
            self.update_tracking()
            ...
        self.animation_layer.update(clock_time)
        #window offset is what I should subtract from mouse events to get the mouse position relative to this element
        return False

    #This is called when the map is changed entirely
    def new_map(self):
        for layer in self.layers:
            layer.new_map()

    #draws this element onto the given surface
    def draw_screen(self,surf):
        surf.fill((0,0,0))
        for layer in self.layers:
            layer.draw(surf,self.map_offset)

    def resize(self,rect):
        super().resize(rect)
        self.pixels_per_grid=min(rect[2],rect[3])//self.grids_per_screen
        self.grid_width=rect[2]//self.pixels_per_grid
        self.grid_height=rect[3]//self.pixels_per_grid
        for layer in self.layers:
            layer.suggest_rerender()

    def load_tilesets(self,fname):
        with open(fname,"r") as f:
            spritesets=yaml.safe_load(f)
            for spriteset in spritesets:
                self.tilesets[spriteset]={} 
                for sprite in spritesets[spriteset]:
                    cell_type=string_to_celltype(sprite)
                    self.tilesets[spriteset][cell_type]=HashedSpriteArray()
                    for elem in spritesets[spriteset][sprite]:
                        self.tilesets[spriteset][cell_type].add_sprite_name(elem[0],elem[1])

    def get_tiles_in_view(self):
        min_x=int(max(self.map_offset[0]//self.pixels_per_grid,0))
        min_y=int(max(self.map_offset[1]//self.pixels_per_grid,0))
        #max_x=int(min(min_x+self.grids_per_screen,self.engine.level.map.width))
        #max_y=int(min(min_y+self.grids_per_screen,self.engine.level.map.height))
        max_x=min(int(min_x+self.grid_width),self.engine.level.map.width-1)
        max_y=min(int(min_y+self.grid_height),self.engine.level.map.height-1)
        return [min_x,min_y,max_x,max_y]
    
    def update_tracking(self):
        player=self.engine.get_player()
        if player is None:
            return
        center_pos=player.get_pos()
        target_x=center_pos.x*self.pixels_per_grid-self.rect[2]//2
        target_y=center_pos.y*self.pixels_per_grid-self.rect[3]//2
        #TODO match target center
        dx=target_x-self.map_offset[0]
        dy=target_y-self.map_offset[1]
        if abs(dx)<self.tracking_slop_grids_x*self.pixels_per_grid:
            dx=0
        if abs(dy)<self.tracking_slop_grids_y*self.pixels_per_grid:
            dy=0
        if dx==0 and dy==0:
            self.turbo_tracking=False
        vx=self.elasticity*dx
        vy=self.elasticity*dy
        maxvel=self.maxvel
        if self.turbo_tracking:
            maxvel=10*maxvel
        if vx>maxvel:
            vx=maxvel
        if vx<-maxvel:
            vx=-maxvel
        if vy>maxvel:
            vy=maxvel
        if vy<-maxvel:
            vy=-maxvel
        self.map_offset=(self.map_offset[0]+vx,self.map_offset[1]+vy)

    def jump_to_tracked(self):
        player=self.engine.get_player()
        if player is None:
            return
        center_pos=player.get_pos()
        self.map_offset=(center_pos.x*self.pixels_per_grid-self.rect[2]//2,center_pos.y*self.pixels_per_grid-self.rect[3]//2)

    def pixel_to_cell(self,pos):
        return MapCoord( (pos[0]+self.map_offset[0])//self.pixels_per_grid,(pos[1]+self.map_offset[1])//self.pixels_per_grid)
    
    def cell_to_pixel(self,cell):
        return ( (cell.x)*self.pixels_per_grid-self.map_offset[0],(cell.y)*self.pixels_per_grid-self.map_offset[1])

    def add_animation(self,animation):
        self.animation_layer.animations.append(animation)
        animation.start()
        return animation
    
    def add_move_animation(self,object_id,start_pos,end_pos,duration):
        ret=MapAnimationMoveObject(self,self.engine,object_id,start_pos,end_pos,duration)
        return self.add_animation(ret)
    
    def deselect(self):
        self.selection_layer.set_selected_cell(None)

    def get_selected_cell(self):
        return self.selection_layer.selected_cell
    
    def handle_engine_message(self,message):
        if message.message_type=="LevelChanged":
            print("level changed message received")
            self.new_map()
            self.selection_layer.set_selected_cell(None)
            pygame.event.post(pygame.event.Event(CELL_SELECTED_EVENT,{"cell": None}))
            self.turbo_tracking=True
        if message.message_type=="MapChanged":
            print("map changed message received")
            self.redraw_needed=True
            self.selection_layer.set_selected_cell(None)
            pygame.event.post(pygame.event.Event(CELL_SELECTED_EVENT,{"cell": None}))
        if message.message_type=="ObjectMoved":
            #lighting may have changed
            self.visibility_layer.suggest_rerender()
            self.cell_color_layer.suggest_rerender()
            self.cell_color_layer.suggest_rerender()
        if message.message_type=="DoorChanged":
            self.wall_layer.suggest_rerender()
            self.cell_color_layer.suggest_rerender()
            self.visibility_layer.suggest_rerender()
