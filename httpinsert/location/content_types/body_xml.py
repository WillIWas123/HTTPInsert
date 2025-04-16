from lxml import etree
from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint


# TODO: Consder writing a custom XML parser....

class Body(Location):
    def traverse_xml(self,element,insertion_points,path=""):
        insertion_points.append(InsertionPoint(self, "body-xml",element.tag.replace("&amp;","&"),element.text.replace("&amp;","&"),key_param=True,default=False))
        if element.attrib:
            keys = {}
            for attr, value in element.attrib.items():
                if attr not in keys.keys():
                    keys[attr] = -1
                keys[attr] += 1

                attr = attr.replace("&amp;","&")
                value = value.replace("&amp;","&")
                insertion_points.append(InsertionPoint(self,"body-xml-attribute",f"{path}/{attr}",value,key_param=True,default=False,index=keys[attr]))
                insertion_points.append(InsertionPoint(self,"body-xml-attribute",f"{path}/{attr}",value,index=keys[attr]))

        if element.text:
            insertion_points.append(InsertionPoint(self,"body-xml",f"{path}/{element.tag.replace('&amp;','&')}",element.text.replace("&amp;","&")))
        for i,child in enumerate(element):
            child_path = f"{path}/{child.tag}[{i}]"
            self.traverse_xml(child,insertion_points,path=child_path)

    def find_insertion_points(self, request):
        insertion_points=[]

        xml_content = request.body.replace("&","&amp;")
        parser = etree.XMLParser(recover=True)
        try:
            tree = etree.fromstring(xml_content.encode('utf-8'), parser)
            if request.body.strip().startswith("<?xml"):
                docinfo = tree.getroottree().docinfo
                insertion_points.append(InsertionPoint(self,"body-xml-version","version",docinfo.xml_version,default=False))
                insertion_points.append(InsertionPoint(self,"body-xml-encoding","encoding",docinfo.encoding,default=False))
                insertion_points.append(InsertionPoint(self,"body-xml-doctype","doctype",docinfo.doctype,default=False))
            self.traverse_xml(tree,insertion_points)
        except Exception as e: 
            pass

        insertion_points.append(InsertionPoint(self, "body","full",request.body,default=False,full=True))
        return insertion_points

    def insert_payload(self,request,insertion_point,payload,default_encoding):
        if insertion_point.full is True:
            request.body = payload
            return request,request.body
        version=False
        if request.body.strip().startswith("<?xml"):
            version=True
        xml_content = request.body.replace("&","&amp;")
        parser = etree.XMLParser(recover=True)

        try:
            tree = etree.fromstring(xml_content.encode('utf-8'),parser)
            docinfo = tree.getroottree().docinfo
        except Exception as e:
            print(f"Your payload does not seem to play nice with XML: {e}")
            return request,request.body

        if insertion_point.location_key == "body-xml-version":
            reconstructed_xml = f'<?xml version="{payload}" encoding="{docinfo.encoding}"?>\n' if version else ""
            if docinfo.doctype:
                reconstructed_xml += docinfo.doctype + "\n"
        elif insertion_point.location_key == "body-xml-encoding":
            reconstructed_xml = f'<?xml version="{docinfo.xml_version}" encoding="{payload}"?>\n' if version else ""
            if docinfo.doctype:
                reconstructed_xml += docinfo.doctype + "\n"
        elif insertion_point.location_key == "body-xml-doctype":
            reconstructed_xml = f'<?xml version="{docinfo.xml_version}" encoding="{docinfo.encoding}"?>\n' if version else ""
            reconstructed_xml += payload+"\n"
        else:
            reconstructed_xml = f'<?xml version="{docinfo.xml_version}" encoding="{docinfo.encoding}"?>\n' if version else ""
            if docinfo.doctype:
                reconstructed_xml += docinfo.doctype + "\n"
            self.insert_payload_xml_body(insertion_point,payload,tree)
        reconstructed_xml += etree.tostring(tree, pretty_print=True, encoding="unicode")
        request.body = reconstructed_xml.replace("&amp;","&").strip()
        return request, request.body

    def insert_payload_xml_body(self,insertion_point, payload, element, path=""):
        if insertion_point.key == element.tag.replace("&amp;","&") and insertion_point.key_param is True:
            element.tag = payload
            return True

        if element.attrib and insertion_point.location_key == "body-xml-attribute":
            keys = {}
            for attr, value in element.attrib.items():
                if attr not in keys.keys():
                    keys[attr] = -1
                keys[attr] += 1
                attr = attr.replace("&amp;","&")
                value = value.replace("&amp;","&")
                if insertion_point.key == f"{path}/{attr}" and insertion_point.index == keys[attr]:
                    if insertion_point.key_param is True:
                        del element.attrib[attr]
                        element.attrib[payload] = value
                        return True

                    else:
                        element.attrib[attr] = payload
                        return True

        if insertion_point.key == f"{path}/{element.tag.replace('&amp;','&')}":
            element.text = payload
            return True
        for i,child in enumerate(element):
            child_path = f"{path}/{child.tag}[{i}]"
            if self.insert_payload_xml_body(insertion_point, payload, child,path=child_path):
                return True

