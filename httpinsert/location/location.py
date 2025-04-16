from abc import ABC, abstractmethod

class Locations:
    locations = []

class Location(ABC):
    def __init__(self):
        for i in Locations.locations:
            if i.__class__.__name__ == self.__class__.__name__: # Prevents duplicates
                break
        else:
            Locations.locations.append(self) # Makes it easy to add new custom locations

    @abstractmethod
    def find_insertion_points(self,request):
        pass

    @abstractmethod
    def insert_payload(self,request,insertion_point,payload,default_encoding):
        pass

    def insert_payloads(self,request,insertion_point,payloads,default_encoding):
        fp = None
        for payload in payloads:
            request,fp = self.insert_payload(request,insertion_point,payload,default_encoding)
        return request,fp

    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self,item):
        if isinstance(item,str): # Can compare location to the name of the class
            return self.__class__.__name__ == item
        return self is item
