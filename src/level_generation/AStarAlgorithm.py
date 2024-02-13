from ..level.MapCoord import MapCoord
from ..level.GraphPaperMap import GraphPaperMap, CellType, WallType

class AStarAlgorithm:
    def __init__(self,the_map):
        self.the_map=the_map

    def find_path(self,start:MapCoord,goal:MapCoord):
        open_set=[start]
        closed_set=[]
        came_from={}
        g_score={}
        f_score={}
        for x in range(self.the_map.width):
            for y in range(self.the_map.height):
                g_score[ MapCoord(x,y)]=float('inf')
                f_score[ MapCoord(x,y)]=float('inf')
        g_score[start]=0
        f_score[start]=self.heuristic_cost_estimate(start,goal)
        while len(open_set)>0:
            current=self.lowest_f_score(open_set,f_score)
            if current==goal:
                return self.reconstruct_path(came_from,goal)
            open_set.remove(current)
            closed_set.append(current)
            for neighbor in self.neighbors(current):
                if neighbor in closed_set:
                    continue
                tentative_g_score=g_score[current]+1+self.cell_weight(neighbor)
                if neighbor not in open_set:
                    open_set.append(neighbor)
                elif tentative_g_score>=g_score[neighbor]:
                    continue
                came_from[neighbor]=current
                g_score[neighbor]=tentative_g_score
                f_score[neighbor]=g_score[neighbor]+self.heuristic_cost_estimate(neighbor,goal)
        return None
    
    def lowest_f_score(self,open_set,f_score):
        lowest=float('inf')
        lowest_cell=None
        for cell in open_set:
            if f_score[cell]<lowest:
                lowest=f_score[cell]
                lowest_cell=cell
        return lowest_cell
    
    def reconstruct_path(self,came_from,current):
        total_path=[current]
        while current in came_from.keys():
            current=came_from[current]
            total_path.insert(0,current)
        return total_path
    
    def heuristic_cost_estimate(self,start,goal):
        return start.manhattan_distance(goal)
        
    def cell_weight(self,cell):
        return 1 #OVERLOAD THIS
    
    def neighbors(self,cell):
        #OVERLOAD THIS
        neighbors=[]
        for direction in range(4):
            if self.the_map.is_passable(cell,direction):
                neighbors.append(cell+self.the_map.direction_to_vector(direction))
        return neighbors
    
class DigPathThroughStone(AStarAlgorithm):
    def __init__(self,the_map,avoid_thin_walls=True):
        super().__init__(the_map)
        self.avoid_thin_walls=avoid_thin_walls

    def cell_weight(self, cell):
        if self.the_map.get_cell_type(cell) in [CellType.INDOOR_FLOOR,CellType.INDOOR_CLEAN_FLOOR]:
            return 1
        elif self.the_map.get_cell_type(cell)==CellType.STONE:
            return 3
        return 1
        
    def neighbors(self,cell):
        neighbors=[]
        obj=self.the_map.get_cell(cell)
        for direction in range(4):
            if obj.walls[direction].wall_type==WallType.NONE:
                new_cell=cell+MapCoord.direction_to_vector(direction)
                if self.the_map.is_on_map(new_cell):
                    if self.avoid_thin_walls==True and self.the_map.get_cell_type(new_cell)==CellType.STONE:
                        #if there is already a wall, don't make it thin
                        new_cell_obj=self.the_map.get_cell(new_cell)
                        wall_types=[ new_cell_obj.walls[0].wall_type,new_cell_obj.walls[1].wall_type,new_cell_obj.walls[2].wall_type,new_cell_obj.walls[3].wall_type]
                        if WallType.WALL in wall_types:
                            continue
                        neighbors.append(new_cell)

                    else:
                        neighbors.append(new_cell)
        return neighbors
    