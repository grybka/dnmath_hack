import random
from .BehaviorTree import BehaviorTree, BehaviorTreeStatus
from ..level.MapCoord import MapCoord, Direction
from ..actions.EntityAction import *

class BTRandomWalk(BehaviorTree):
    #Walk around randomly forever
    def __init__(self,parent=None):
        super().__init__(parent)
        
    def act(self,agent,engine):
        if random.random()<0.5:
            engine.set_entity_action(agent.id,MoveAction(agent,engine,random.choice(MapCoord.all_directions())))
        else:
            engine.set_entity_action(agent.id,WaitAction(agent,engine))
        return BehaviorTreeStatus.RUNNING
        #return BehaviorTreeStatus.SUCCESS
    

class BTChasePlayer(BehaviorTree):
    #Chase the player
    def __init__(self,parent=None):
        super().__init__(parent)
        
    def act(self,agent,engine):
        #see if the player is in my vision
        visible_cells=agent.get_visible_cells(engine.level.map)
        objects=engine.level.map.get_objects_in_cells(visible_cells)
        player=engine.get_player()
#        print("objects are ",objects)
        text=[obj.reference_noun() for obj in objects]
#        print("objects are {}".format(text))
        if player in objects:
            #get the direction to the player
            player_pos=player.get_pos()
            my_pos=agent.get_pos()
            if player_pos.x < my_pos.x:
                direction=Direction.W
            elif player_pos.x > my_pos.x:
                direction=Direction.E
            elif player_pos.y < my_pos.y:
                direction=Direction.N
            elif player_pos.y > my_pos.y:
                direction=Direction.S
            else:
                return BehaviorTreeStatus.SUCCESS
            engine.set_entity_action(agent.id,MoveAction(agent,engine,direction))
            return BehaviorTreeStatus.RUNNING
        else:
            return BehaviorTreeStatus.FAILURE        