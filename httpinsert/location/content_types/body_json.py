import json
from httpinsert.location import Location
from httpinsert.insertion_points import InsertionPoint

# TODO: Consider writing a custom json parser...

class Body(Location):
    def find_insertion_points(self, request):
        insertion_points=[]
        def extract_json_insertion_points(data, parent_key=""):
            points = []
            if isinstance(data, dict):
                for k, v in data.items():
                    full_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, (dict, list)):
                        points.append(InsertionPoint(self,"body-json",full_key,json.dumps(v),key_param=True,default=False)) 
                        points.extend(extract_json_insertion_points(v, full_key))
                    else:
                        points.append(InsertionPoint(self,"body-json",full_key,v,key_param=True,default=False)) 
                        points.append(InsertionPoint(self, "body-json", full_key, v))
                points.append(InsertionPoint(self, "body-json",parent_key, "1",new_param=True,default=False))
            elif isinstance(data, list):
                for idx, item in enumerate(data):
                    full_key = f"{parent_key}[{idx}]"
                    if isinstance(item, (dict, list)):
                        points.append(InsertionPoint(self,"body-json",full_key,json.dumps(item)))
                        points.extend(extract_json_insertion_points(item, full_key))
                    else:
                        points.append(InsertionPoint(self, "body-json", full_key, json.dumps(item)))
            else:
                points.append(InsertionPoint(self, "body-json",str(type(data)),data))
            return points

        try:
            json_data = json.loads(request.body)
            insertion_points.extend(extract_json_insertion_points(json_data))
        except Exception:
            pass
        insertion_points.append(InsertionPoint(self, "body","full",request.body,full=True,default=False))
        return insertion_points

    def insert_payload(self,request,insertion_point,payload,default_encoding):
        if default_encoding is True:
            payload=payload.replace("\"","\\\"") # Making sure the payload works as a JSON value
        def update_json_with_payload(data, target_key, payload):
            main_data=data
            keys = target_key.split('.')
            for idx, key in enumerate(keys):
                if key == str(type("a")) or key == str(type(True)) or key == str(type(1)):
                    return payload
                elif key.endswith(']') and '[' in key:
                    base_key, index = key[:-1].split('[')
                    index = int(index)
                    if idx == len(keys) - 1:
                        if isinstance(data, list):
                            if insertion_point.new_param is True and isinstance(data[index],dict):
                                data[index][payload] = insertion_point.value
                            else:
                                data[index] = payload
                        else:
                            data[base_key][index] = payload
                    else:
                        data = data[index] if isinstance(data, list) else data[base_key][index]
                elif idx == len(keys) - 1:
                    if insertion_point.new_param is True:
                        data[payload] = insertion_point.value
                    elif isinstance(data, list):
                        data[int(key)] = payload
                    else:
                        if insertion_point.key_param is True:
                            data[payload] = data[key]
                            del data[key]
                        else:
                            data[key] = payload
                else:
                    data = data[int(key)] if isinstance(data, list) else data[key]
            return main_data
        json_data = json.loads(request.body)
        json_data = update_json_with_payload(json_data, insertion_point.key, payload)
        request.body=json.dumps(json_data).encode()
        return request,request.body
