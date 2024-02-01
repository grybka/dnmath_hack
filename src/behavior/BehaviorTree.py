from enum import Enum
import random

class BehaviorTreeStatus(Enum):
    SUCCESS = 0
    FAILURE = 1
    RUNNING = 2
    ERROR = 3

class BehaviorTree:
    def __init__(self,parent=None):
        self.parent=parent
        
    def act(self,agent,engine):
        return BehaviorTreeStatus.ERROR #should be overridden by subclasses
    
class BehaviorTreeSequence(BehaviorTree):
    def __init__(self,children,parent=None):
        super().__init__(parent)
        self.children=children
        self.current_child=0
        
    def act(self,agent,engine):
        if self.current_child>=len(self.children):
            return BehaviorTreeStatus.SUCCESS
        child_status=self.children[self.current_child].act(agent,engine)
        if child_status==BehaviorTreeStatus.SUCCESS:
            self.current_child+=1
            if self.current_child>=len(self.children):
                return BehaviorTreeStatus.SUCCESS
            else:
                return BehaviorTreeStatus.RUNNING
        elif child_status==BehaviorTreeStatus.RUNNING:
            return BehaviorTreeStatus.RUNNING
        else:
            return BehaviorTreeStatus.FAILURE
