from urllib.parse import urlunparse, quote,urlparse
from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint

class Path(Location):

    def find_insertion_points(self,request):
        insertion_points=[]
        parsed_url = urlparse(request.url)
        path = parsed_url.path
        segments = path.strip("/").split("/")
        for idx, segment in enumerate(segments):
            insertion_points.append(InsertionPoint(self,"path", str(idx), segment,default=False))
        if path != "/" and path[-1] == "/":
            insertion_points.append(InsertionPoint(self,"path",str(idx+1),"",default=False,new_param=True))
        return insertion_points


    def insert_payload(self,request,insertion_point,payload,default_encoding):
        if default_encoding is True:
            if isinstance(payload,str):
                payload=quote(payload) # Encode the payload
            else:
                payload = [quote(i) for i in payload]
        parsed_url = urlparse(request.url)
        path = parsed_url.path
        segments = path.strip("/").split("/")
        if int(insertion_point.key) == len(segments):
            path+=payload
        else:
            segments[int(insertion_point.key)] = payload
            path = quote("/" + "/".join(segments))
        url = urlunparse(parsed_url._replace(path=path))
        request.url=url
        return request,request.url


Path()
