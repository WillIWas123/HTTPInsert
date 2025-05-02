from urllib.parse import urlunparse, quote,urlparse
from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint
from httpinsert import Headers

class Manual(Location):

    def find_insertion_points(self,request):
        insertion_points=[]

        parsed_url = urlparse(request.url)
        # Find manual path parameters
        path = parsed_url.path

        # TODO: Consider parsing manual insertion points in a different manner
        for c,_ in enumerate(range(parsed_url.path.count("FUZZ"))):
            path = path.replace("FUZZ",f"FUZ{c}Z",1)
            insertion_points.append(InsertionPoint(self,"path", f"FUZ{c}Z",""))


        # Find manual query parameters
        query = parsed_url.query
        for c,_ in enumerate(range(parsed_url.query.count("FUZZ"))):
            query = query.replace("FUZZ",f"FUZ{c}Z",1)
            insertion_points.append(InsertionPoint(self,"query", f"FUZ{c}Z", ""))
        request.url = urlunparse(parsed_url._replace(query=query,path=path))


        # Find manual header parameters
        new_headers=Headers()
        c = 0
        for k,v in request.headers.items():
            new_k=k
            new_v=v
            if "FUZZ" in k:
                count = k.count("FUZZ")
                for c2 in range(c,count+c):
                    new_k = new_k.replace("FUZZ",f"FUZ{c2}Z",1)
                    insertion_points.append(InsertionPoint(self,"header",f"FUZ{c2}Z",""))
                if "FUZZ" not in v:
                    new_headers[new_k] = v
                c+=count
            if "FUZZ" in v:
                count = v.count("FUZZ")
                for c2 in range(c,count+c):
                    new_v = new_v.replace("FUZZ",f"FUZ{c2}Z",1)
                    insertion_points.append(InsertionPoint(self,"header",f"FUZ{c2}Z",""))
                new_headers[new_k] = new_v
                c+=count
            if "FUZZ" not in k and "FUZZ" not in v:
                new_headers[k]=v
        request._headers=new_headers

        # Find manual body parameters
        new_body=request.body
        if request.body:
            for c,_ in enumerate(range(request.body.count(b"FUZZ"))):
                new_body=new_body.replace(b"FUZZ",f"FUZ{c}Z".encode(),1)
                insertion_points.append(InsertionPoint(self,"body", f"FUZ{c}Z".encode(), ""))
            request.body=new_body

        return insertion_points

    def insert_payload(self,request,insertion_point,payload,default_encoding):
        if insertion_point.location_key == "query":
            return self.insert_payload_query(request,insertion_point,payload,default_encoding)
        elif insertion_point.location_key == "path":
            return self.insert_payload_path(request,insertion_point,payload,default_encoding)
        elif insertion_point.location_key == "header":
            return self.insert_payload_header(request,insertion_point,payload,default_encoding)
        elif insertion_point.location_key == "body":
            return self.insert_payload_body(request,insertion_point,payload,default_encoding)

    def insert_payload_query(self,request,insertion_point,payload,default_encoding):
        if default_encoding is True:
            payload = quote(payload)
        parsed_url = urlparse(request.url)
        modified_query=parsed_url.query.replace(insertion_point.key,payload)
        url = urlunparse(parsed_url._replace(query=modified_query))
        request.url=url
        return request, request.url

    def insert_payload_path(self,request,insertion_point,payload,default_encoding):
        if default_encoding is True:
            payload = quote(payload)
        parsed_url = urlparse(request.url)
        modified_path = parsed_url.path.replace(insertion_point.key,payload)
        url = urlunparse(parsed_url._replace(path=modified_path))
        request.url=url
        return request,request.url

    def insert_payload_header(self,request,insertion_point,payload,default_encoding):
        headers = Headers()
        for k,v in request.headers.items():
            if insertion_point.key in k:
                k = k.replace(insertion_point.key,payload)
            if insertion_point.key in v:
                v = v.replace(insertion_point.key,payload)
            headers[k] = v
        request._headers=headers
        return request,headers

    def insert_payload_body(self,request,insertion_point,payload,default_encoding):
        if default_encoding is True:
            payload=quote(payload)
        modified_body = request.body.replace(insertion_point.key,payload.encode())
        request.body=modified_body
        return request,modified_body

Manual()
