import re
from httpinsert import Headers
from httpinsert.formatter import PayloadFormatter

def find_insertion_points(request,location=None,location_key=None,key=None,value=None,new_param=None,key_param=None,default=None,full=None,index=None):
    from httpinsert.location import Locations # Prevent import recursion
    insertion_points = []
    for loc in Locations.locations:
        if location is not None and loc != location:
            continue
        new_insertion_points = loc.find_insertion_points(request)
        for insertion_point in new_insertion_points:
            if location is not None and insertion_point.location != location: # Redundant
                continue
            if location_key is not None and insertion_point.location_key != location_key:
                continue
            if key is not None and insertion_point.key != key:
                continue
            if value is not None and insertion_point.value != value:
                continue
            if new_param is not None and insertion_point.new_param != new_param:
                continue
            if key_param is not None and insertion_point.key_param != key_param:
                continue
            if default is not None and insertion_point.default != default:
                continue
            if full is not None and insertion_point.full != full:
                continue
            if index is not None and insertion_point.index != index:
                continue
            insertion_points.append(insertion_point)

    return insertion_points

def insert_payload(request, insertion_point, payload,default_encoding=True,format_payload=False):
    return insertion_point.insert(request,payload,default_encoding=default_encoding,format_payload=format_payload)

def remove_placeholders(request):
    if isinstance(request,str):
        return re.sub(r"FUZ\d*Z","",request)
    elif isinstance(request,bytes):
        return re.sub(rb"FUZ\d*Z",b"",request)
    elif isinstance(request,Headers) or isinstance(request,dict):
        new_headers = Headers()
        for k,v in request.items():
            new_headers[re.sub(r"FUZ\d*Z","",k)] = re.sub(r"FUZ\d*Z","",v)
        return new_headers

    request.url=re.sub(r"FUZ\d*Z","",request.url)
    if request.body:
        request.body=re.sub(rb"FUZ\d*Z",b"",request.body)
    new_headers=Headers()
    for k,v in request.headers.items():
        k = re.sub(r"FUZ\d*Z","",k)
        v = re.sub(r"FUZ\d*Z","",v)
        new_headers[k] = v
    request._headers=new_headers
    return request

class InsertionPoint:
    def __init__(self, location, location_key, key, value,new_param=False,key_param=False,default=True,full=False,index=-1):
        self.location = location
        self.location_key = location_key
        self.key = key
        self.value = value
        self.payload_formatter = PayloadFormatter()
        self.new_param = new_param # Is this a new param, or a modified param?
        self.key_param = key_param # Is this param a "key" or a "value"?
        self.default = default # Should this be considered a default param?
        self.full=full
        self.index=index
        """
            Non-default params:
                method
                path
                query-key
                version
                header-key
                any body-key
                any new_param

        """

    def insert(self,payload,request,format_payload=False,default_encoding=True):
        return Insertion(self,payload,request,format_payload=format_payload,payload_formatter=self.payload_formatter,default_encoding=default_encoding)

    def __repr__(self):
        attributes = [
            f"location={self.location}",
            f"location_key={self.location_key}",
            f"key={self.key}",
        ]

        if self.value:
            attributes.append(f"value={self.value}")
        if self.default is False:
            attributes.append("default=False")
        if self.full:
            attributes.append("full=True")
        if self.key_param:
            attributes.append("key_param=True")
        if self.new_param is True:
            attributes.append("new_param=True")
        if self.index > 0:
            attributes.append(f"index={self.index}")

        return f"<InsertionPoint {' '.join(attributes)}>"

class Insertion:
    def __init__(self,insertion_point,payload,req,format_payload=False,payload_formatter=None,default_encoding=True):
        self.default_encoding=default_encoding # Should we use the default encoding, False means no encoding at all
        self.payload=payload
        self.default_encoding = default_encoding
        self.full_section = None
        if format_payload is True:
            payload_formatter = payload_formatter or PayloadFormatter()
            self.payload = payload_formatter.format(payload,old=str(insertion_point.value))
        self.insertion_point=insertion_point
        self.req=req.copy()

    def insert_request(self,request):
        request, full_section = self.insertion_point.location.insert_payload(request,self.insertion_point,self.payload,self.default_encoding)
        self.full_section = remove_placeholders(full_section)
        return request

    def send(self, **kwargs):
        return self.req.send(insertions=[self],**kwargs)
