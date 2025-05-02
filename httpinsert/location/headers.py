from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint
from httpinsert import Headers as RequestHeaders

class Headers(Location):
    def find_insertion_points(self,request):
        insertion_points=[]

        keys = {}
        for key, value in request.headers.items():
            if key not in keys.keys():
                keys[key] = -1
            keys[key] += 1
            if key.lower() == "cookie":
                insertion_points.extend(self.find_insertion_points_cookies(request))
                continue
            insertion_points.append(InsertionPoint(self,"header",key,value,index=keys[key],key_param=True,default=False))
            insertion_points.append(InsertionPoint(self,"header", key, value,index=keys[key]))
        insertion_points.append(InsertionPoint(self,"header", "", "1",new_param=True,default=False))
        return insertion_points


    def insert_payload(self,request,insertion_point,payload,default_encoding):
        # TODO: look at default encoding
        headers = request.headers

        if insertion_point.new_param is True:
            headers._headers[payload] = [insertion_point.value]
            request._headers = headers
            return request, headers

        headers_out = RequestHeaders()

        keys = {}
        for k, v in headers.items():
            if k not in keys.keys():
                keys[k] = -1
            keys[k]+=1
            if k == insertion_point.key and keys[k] == insertion_point.index:
                if insertion_point.key_param is True:
                    headers_out[payload] = insertion_point.value
                else:
                    headers_out[insertion_point.key] = payload

            else:
                headers_out[k] = v
            
        request._headers=headers_out
        return request,headers_out

    def insert_payloads(self,request,insertion_point,payloads,default_encoding):
        headers = request.headers
        if insertion_point.new_param is True:
            for payload in payloads:
                headers[payload] = insertion_point.value
            request._headers = headers
            return request, headers

        full_section = None
        for payload in payloads:
            request, full_section = self.insert_payload(request,insertion_point,payload,default_encoding)
        return request, full_section



    def find_insertion_points_cookies(self,request): # Edge-case, finding cookie params here to keep order of insertion points correct
        insertion_points=[]

        keys = {}
        for key, value in request.cookies.items():
            if key not in keys.keys():
                keys[key] = -1
            keys[key] += 1
            insertion_points.append(InsertionPoint(self,"cookie",key, value,index=keys[key],key_param=True,default=False))
            insertion_points.append(InsertionPoint(self,"cookie", key,value,index=keys[key]))
        insertion_points.append(InsertionPoint(self,"cookie", "", "1",new_param=True,default=False))
        return insertion_points


Headers()
