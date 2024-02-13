#random table like structure
#To Model something typicaly like
#roll 1d6
#1-2:  1d4 goblins and 1d2 orcs
#3: 1d6 orcs
#4: 3 rats
import random

class RandomQuantity:
    def __init__(self,text):
        #kwargs is either
        # text: "1d6"
        # or
        # number: 6
        self.number=None
        self.ndice=None
        self.dicesize=None
        self.parse_text(text)
        

    def parse_text(self,text):
        if "d" in text:
            first,second=text.split("d")
            self.ndice=int(first)
            self.dicesize=int(second)
        else:
            self.number=int(text)

    def realize(self):
        if self.number is not None:
            return self.number
        else:
            the_number=0
            for i in range(self.ndice):
                the_number+=random.randint(1,self.dicesize)
            return the_number

class TableEntry:
    def __init__(self):
        ...

    def realize(self):
        #return a list of pairs of (object,quantity)
        raise NotImplementedError("Table Entry not implemented")
        ...

class TableEntryAnd:
    def __init__(self,entries):
        self.entries=entries

    def realize(self):
        results=[]
        for entry in self.entries:
            results.extend(entry.realize())
        return results

class TableEntryObjects:
    def __init__(self,object,quantity):
        self.object=object
        self.quantity=quantity

    def realize(self):
        return [(self.object,self.quantity.realize())]
    
def parse_table_entry(text):
    split_by_and=text.split(" and ")
    entries=[]
    for entry in split_by_and:
        q,o=entry.split(" ")
        quantity=RandomQuantity(text=q)
        entries.append(TableEntryObjects(object=o,quantity=quantity))
    if len(entries)==1:
        return entries[0]
    else:
        return TableEntryAnd(entries)
    
class RandomTable:
    def __init__(self):
        self.entries=[] #tablentry, weight
        self.weights=[]

    def add_entry(self,entry,weight=1):
        self.entries.append( entry )
        self.weights.append(weight)

    def realize(self):
        #return a list of pairs of (object,quantity)
        chosen_entry=random.choices(self.entries,weights=self.weights)[0]
        return chosen_entry.realize()
    

def parse_random_table_from_array(array):
    table=RandomTable()
    for entry in array:
        entry=entry.strip()
        if entry=="":
            continue
        weight,entry=entry.split(":")
        table.add_entry(parse_table_entry(entry.strip()),weight=int(weight))
    return table

def parse_random_table(text):
    table=RandomTable()
    entries=text.split("\n")
    return parse_random_table_from_array(entries)


    
if __name__=="__main__":
    test_table="""
    1: 1 goblin
    2: 1d6 goblins
    1: 1d6 goblins and 1d2 orcs
    """
    #entry=parse_table_entry("1 goblin")
    #print(entry.realize())
    #entry=parse_table_entry("1d6 goblins")
    #print(entry.realize())
    #entry=parse_table_entry("1d6 goblins and 1d2 orcs")
    #print(entry.realize())
    table=parse_random_table(test_table)
    print(table.realize())