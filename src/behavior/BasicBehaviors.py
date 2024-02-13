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
            all_moves={}
            for dir in MapCoord.all_directions():
                all_moves[dir]=MoveAction(agent,engine,dir)
            if player_pos.x < my_pos.x and all_moves[Direction.W].is_possible():
                direction=Direction.W
            elif player_pos.x > my_pos.x and all_moves[Direction.E].is_possible():
                direction=Direction.E
            elif player_pos.y < my_pos.y and all_moves[Direction.N].is_possible():
                direction=Direction.N
            elif player_pos.y > my_pos.y and all_moves[Direction.S].is_possible():
                direction=Direction.S
            else:
                return BehaviorTreeStatus.SUCCESS
            engine.set_entity_action(agent.id,MoveAction(agent,engine,direction))
            return BehaviorTreeStatus.RUNNING
        else:
            return BehaviorTreeStatus.FAILURE        
        
#ranged attack
class BTRangedAttackPlayer(BehaviorTree):
    #Attack the player
    def __init__(self,parent=None):
        super().__init__(parent)
        
    def act(self,agent,engine):
        #see if the player is in my vision
        player=engine.get_player()
        visible_cells=agent.get_visible_cells(engine.level.map)
        objects=engine.level.map.get_objects_in_cells(visible_cells)
        if player in objects:
            #get the direction to the player
            #layer_pos=player.get_pos()
            #my_pos=agent.get_pos()
            maction=RangedAttackAction(agent,engine,player)
            if maction.is_possible()[0]:
                engine.set_entity_action(agent.id,maction)
                return BehaviorTreeStatus.SUCCESS
        return BehaviorTreeStatus.FAILURE


#ranged attack
class BTMeleeAttackPlayer(BehaviorTree):
    #Attack the player
    def __init__(self,parent=None):
        super().__init__(parent)
        
    def act(self,agent,engine):
        #see if the player is in my vision
        player=engine.get_player()
        visible_cells=agent.get_visible_cells(engine.level.map)
        objects=engine.level.map.get_objects_in_cells(visible_cells)
        if player in objects:
            #get the direction to the player
            #layer_pos=player.get_pos()
            #my_pos=agent.get_pos()
            maction=MeleeAction(agent,engine,player)
            if maction.is_possible()[0]:
                engine.set_entity_action(agent.id,maction)
                return BehaviorTreeStatus.SUCCESS
        return BehaviorTreeStatus.FAILURE