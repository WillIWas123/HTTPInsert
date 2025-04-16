from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint

class Method(Location):
    def find_insertion_points(self,request):
        return [InsertionPoint(self,"method",request.method,request.method,default=False)]

    def insert_payload(self,request,insertion_point,payload,default_encoding):
        request.method=payload
        return request,request.method

Method()
