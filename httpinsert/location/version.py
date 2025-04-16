from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint

class Version(Location):
    def find_insertion_points(self,request): # include_new and include_key does nothing here
        return [InsertionPoint(self,"version",request.version,request.version,default=False)]

    def insert_payload(self,request,insertion_point,payload,default_encoding): 
        if "HTTP" not in payload:
            payload = f"HTTP/{payload}"
        request.version=payload
        return request,request.version

Version()
