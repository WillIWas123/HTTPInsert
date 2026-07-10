from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint

class SNI(Location):
    def find_insertion_points(self,request):
        value = request.sni or request.host
        return [InsertionPoint(self,"sni",value,value,default=False)]

    def insert_payload(self,request,insertion_point,payload,default_encoding):
        request.sni = payload
        return request,request.sni

SNI()
