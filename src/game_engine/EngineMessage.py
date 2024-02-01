class EngineMessage:
     def __init__(self,messagetype="EngineMessage"):
        self.message_type=messagetype

class EMActionFailed(EngineMessage):
      def __init__(self,reason):
         self.message_type="ActionFailed"
         self.reason=reason

class EMObjectMoved(EngineMessage):
    def __init__(self,objid,oldpos,pos):
        self.message_type="ObjectMoved"
        self.objid=objid
        self.pos=pos
        self.oldpos=oldpos

class EMInfoText(EngineMessage):
    def __init__(self,text):
        self.message_type="InfoText"
        self.text=text

class EMMapChanged(EngineMessage):
    def __init__(self):
        self.message_type="MapChanged"

class PlayerInventoryChanged(EngineMessage):
    def __init__(self):
        self.message_type="PlayerInventoryChanged"

class EMMeleeAttack(EngineMessage):
    def __init__(self,attacker,defender,damage,message):
        self.message_type="MeleeAttack"
        self.attacker=attacker
        self.defender=defender
        self.message=message
        self.damage=damage

class EMRangedAttack(EngineMessage):
    def __init__(self,attacker,defender,damage,message,ammotype,start_pos,end_pos):
        self.message_type="RangedAttack"
        self.attacker=attacker
        self.defender=defender
        self.message=message
        self.damage=damage
        self.start_pos=start_pos
        self.end_pos=end_pos
        self.ammotype=ammotype #this is used to figure out which sprite to show

class EMCreatureDeath(EngineMessage):
    def __init__(self,creature,cell_pos):
        self.message_type="CreatureDeath"
        self.creature=creature
        self.cell_pos=cell_pos