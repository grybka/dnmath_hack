import yaml

from .GameObject import gameobject_constructors

def create_gameobject(object):
    if "type" in object:
        if object["type"] in gameobject_constructors:
            #print("creating object {}".format(object))
            return gameobject_constructors[object["type"]](object=object)
    raise Exception("Unknown game object type: "+object["type"])

class GameObjectTemplate:
    def __init__(self,object={},parent=None):
        self.object=object
        #print("template data {}".format(object))
        self.parent=object.get("parent",parent)

    def __getitem__(self,key):
        if key in self.object:
            return self.object[key]
        elif self.parent is not None:
            return self.parent[key]
        else:
            raise KeyError("Key not found: "+key)

    def __contains__(self,key):
        if key in self.object:
            return True
        elif self.parent is not None:
            return key in self.parent
        else:
            return False

    def get(self,key,default=None):
        if key in self:
            return self[key]
        elif self.parent is not None:
            if key in self.parent:
                return self.parent[key]
        return default
    
    def __str__(self):
        ret="GameObjectTemplate: \n"
        ret+=str(self.object)+"\n"
        ret+="Parent: \n"
        ret+=str(self.parent)
        return ret

class GameObjectFactory:
    def __init__(self):
        self.templates={}

    def load_templates(self,filename):
        with open(filename,"r") as f:
            template_data=yaml.safe_load(f)
            for template_name in template_data:
                self.templates[template_name]=GameObjectTemplate(template_data[template_name])

    def create_object(self,template_name,object={}):
        if template_name in self.templates:
            temp_template=GameObjectTemplate(object,self.templates[template_name])
            ret=create_gameobject(temp_template)
            #special cases things in things need to be instantiated
            if "contents" in temp_template:
                for content in temp_template["contents"]:
                    obj_data=content.get("object_data",{})
                    ret.add_object(self.create_object(content["type"],obj_data))
#            ret.populate_subobjects()
            ret.template_type=template_name
            return ret
        else:
            raise Exception("Unknown template: "+template_name)
            return None

__object_factory=GameObjectFactory()
def create_object_from_template(template_name,data={}):
    return __object_factory.create_object(template_name,data)

def load_object_templates(filename):
    __object_factory.load_templates(filename)