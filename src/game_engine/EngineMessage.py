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

class EMRoomChanged(EngineMessage):
    def __init__(self,actor,old_room,new_room,message=""):
        self.message_type="RoomChanged"
        self.old_room=old_room
        self.new_room=new_room
        self.actor=actor
        self.message=message

class EMLevelChanged(EngineMessage):
    def __init__(self,level,level_name):
        self.message_type="LevelChanged"
        self.level_name=level_name
        self.level=level

#this is for a message on something that's read
class EMReadMessage(EngineMessage):
    def __init__(self,reader,target,text,prompted=False):
        self.message_type="ReadMessage"
        self.reader=reader
        self.target=target #a creature or None
        self.text=text
        self.prompted=prompted

class EMDoorChangedMessage(EngineMessage):
    def __init__(self,door,open):
        self.message_type="DoorChanged"
        self.door=door
        self.open=open