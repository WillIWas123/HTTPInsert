from urllib.parse import parse_qsl, urlencode
from httpinsert.location import Location, Manual
from .content_types import BodyJSON, BodyXML, BodyFormUrlencoded

class Body(Location):

    def __init__(self):
        super().__init__()
        self.json = BodyJSON()
        self.xml = BodyXML()
        self.form_urlencoded = BodyFormUrlencoded()
        self.manual = Manual()

    def find_insertion_points(self,request):
        output = []
        content_type = request.headers.get("Content-Type")
        if content_type is None:
            return output
        if content_type == "application/x-www-form-urlencoded":
            output.extend(self.form_urlencoded.find_insertion_points(request))
        elif content_type == "application/xml":
            output.extend(self.xml.find_insertion_points(request))
        elif content_type == "application/json":
            output.extend(self.json.find_insertion_points(request))
        return output

    def insert_payload(self,request,insertion_point,payload,default_encoding):
        if insertion_point.location_key == "body":
            return self.form_urlencoded.insert_payload(request,insertion_point,payload,default_encoding)

        elif insertion_point.location_key == "body-manual":
            return self.manual.insert_payload(request,insertion_point,payload,default_encoding)

        elif insertion_point.location_key == "body-json":
            return self.json.insert_payload(request,insertion_point,payload,default_encoding)

        elif insertion_point.location_key.startswith("body-xml"):
            return self.xml.insert_payload(request,insertion_point,payload,default_encoding)
        else:
            raise NotImplementedError("Location '{insertion_point.location_key}' is not implemented!")

        return request,request.body

# TODO: implement insertion_payloads for performance gains

Body()
