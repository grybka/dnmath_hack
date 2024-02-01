import uuid

#these are the objects that are in a level
class ObjectStore:
    def __init__(self):
        self.objects={} #sorted by id

    def add_object(self,obj):
        obj.object_store=self
        self.objects[obj.id]=obj

    def get_object(self,obj_id:uuid.UUID):
        if obj_id not in self.objects:
            return None
        return self.objects[obj_id]

    def delete_object(self,obj_id:uuid.UUID):
        del self.objects[obj_id]

    def get_object_ids_of_class(self,classname):
        return [obj.id for obj in self.objects.values() if isinstance(obj,classname)]