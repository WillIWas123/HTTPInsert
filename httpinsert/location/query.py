from urllib.parse import parse_qsl, urlencode, urlunparse, quote,urlparse
from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint

class Query(Location):

    def find_insertion_points(self,request):
        insertion_points=[]
        parsed_url = urlparse(request.url)
        query_params = parse_qsl(parsed_url.query,keep_blank_values=True)
        keys = {}
        for key, value in query_params: 
            if key not in keys.keys():
                keys[key] = -1
            keys[key] += 1
            insertion_points.append(InsertionPoint(self,"query", key, value,index=keys[key],key_param=True,default=False))
            insertion_points.append(InsertionPoint(self,"query", key,value,index=keys[key]))
        insertion_points.append(InsertionPoint(self,"query", "", "1",new_param=True,default=False))
        return insertion_points


    def insert_payload(self,request,insertion_point,payload,default_encoding):
        if default_encoding is True:
            payload=quote(payload) # Encode the payload

        parsed_url = urlparse(request.url)
        query_params = parse_qsl(parsed_url.query,keep_blank_values=True)

        modified_query = []

        if insertion_point.new_param is True:
            modified_query = query_params
            modified_query.append((payload, insertion_point.value))
        else:
            keys = {}

            for key,value in query_params:
                if key not in keys.keys():
                    keys[key] = -1
                keys[key] += 1
                if key == insertion_point.key and keys[key] == insertion_point.index:
                    if insertion_point.key_param is True:
                        modified_query.append((payload,insertion_point.value))
                    else:
                        modified_query.append((key,payload))
                else:
                    modified_query.append((key,value))

        quote_via=lambda a,*args,**kwargs:a # Removes any URL encoding affecting the rest of the query
        query = urlencode(modified_query, doseq=True,quote_via=quote_via)
        url = urlunparse(parsed_url._replace(query=query))
        request.url=url
        return request, request.url

    def insert_payloads(self,request,insertion_point,payloads,default_encoding):
        if default_encoding is True:
            payloads = [quote(payload) for payload in payloads]

        parsed_url = urlparse(request.url)
        query_params = parse_qsl(parsed_url.query,keep_blank_values=True)

        if insertion_point.new_param is False:
            # This does not make a lot of sense, but does not break anything at least...
            for payload in payloads:
                request,_ = self.insert_payload(request,insertion_point,payload,default_encoding)
            return request, request.url

        for payload in payloads:
            query_params.append((payload, insertion_point.value))

        quote_via=lambda a,*args,**kwargs:a
        query = urlencode(query_params, doseq=True,quote_via=quote_via)
        url = urlunparse(parsed_url._replace(query=query))
        request.url=url

        return request, request.url


Query()
