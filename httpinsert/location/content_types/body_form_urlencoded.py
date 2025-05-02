from urllib.parse import parse_qsl, urlencode,quote
from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint

class Body(Location):
    def find_insertion_points(self,request):
        insertion_points=[]
        body_params = parse_qsl(request.body,keep_blank_values=True)
        keys = {}
        for key, value in body_params:
            if key not in keys.keys():
                keys[key] = -1
            keys[key]+=1
            insertion_points.append(InsertionPoint(self,"body",key,value,index=keys[key],key_param=True,default=False))
            insertion_points.append(InsertionPoint(self,"body",key,value,index=keys[key]))
        insertion_points.append(InsertionPoint(self,"body", "", b"1",new_param=True,default=False))
        insertion_points.append(InsertionPoint(self,"body","full",request.body,default=False,full=True)) # Modify the entire body at once
        return insertion_points



    def insert_payload(self,request,insertion_point,payload,default_encoding):
        if default_encoding is True:
            if isinstance(payload,str):
                payload=quote(payload) # Encode the payload

        payload = payload.encode()
        if insertion_point.full is True:
            request.body=payload
            return request,request.body

        body_params = parse_qsl(request.body,keep_blank_values=True)

        if insertion_point.new_param is True:
            modified_body = body_params
            modified_body.append((payload,insertion_point.value))
        else:
            modified_body = []
            keys = {}
            for key,value in body_params:
                if key not in keys.keys():
                    keys[key] = -1
                keys[key] += 1
                if key == insertion_point.key and keys[key] == insertion_point.index:
                    if insertion_point.key_param is True:
                        modified_body.append((payload,value))
                    else:
                        modified_body.append((key,payload))
                else:
                    modified_body.append((key,value))

        parts = []
        for key,value in modified_body:
            parts.append(key + b"=" + value)

        request.body=b"&".join(parts)
        return request,request.body
