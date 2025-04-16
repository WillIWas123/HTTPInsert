from httpinsert.location import Location

class Cookies(Location):
    def find_insertion_points(self,request):
        return [] # Edge-case, this is handled in headers

    def insert_payload(self,request,insertion_point,payload,default_encoding):
        # TODO: look at default encoding
        cookies = request.cookies

        if insertion_point.new_param is True:
            cookies[payload] = insertion_point.value
            request._cookies = cookies
            return request, headers

        cookies_out = {}

        keys = {}
        for k,v in cookies.items():
            if k not in keys.keys():
                keys[k] = -1
            keys[k] += 1

            if k == insertion_point.key and keys[k] == insertion_point.index:
                if insertion_point.key_param is True:
                    cookies_out[payload] = insertion_point.value
                else:
                    cookies_out[insertion_point.key] = payload
            else:
                cookies_out[k] = v
        headers = request.headers
        headers._headers["Cookie"] = ["; ".join(f"{k}={v}" for k, v in cookies.items())]
        request._headers=headers
        return request,headers

Cookies()
