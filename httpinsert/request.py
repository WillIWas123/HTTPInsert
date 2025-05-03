import requests
import random
import time
from urllib.parse import urlparse, parse_qs
import json
import http
import urllib3
from http.client import HTTPConnection
import sys
from httpinsert import Headers
from httpinsert.insertion_points import remove_placeholders
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

requests.utils._validate_header_part = lambda a,b,c: None # Disables verification of header names in requests
http.client._is_legal_header_name = lambda a:True # Disables verification of header names in urllib3

def raw_request(scheme,data):
    
    lines = data.split(b"\n")
    # Keeping version here for future reference when urllib starts supporting HTTP2
    method, path, version = lines[0].decode().split()
    
    headers = Headers()
    host = None
    body = None 
    for c, line in enumerate(lines[1:]):
        if not line:
            body = b"\n".join(lines[c+2:])
            break
        key,value = line.split(b":", 1)
        if key.strip().lower() == b"host":
            host = value.strip().decode()
            continue # Don't add Host header to the headers, this will cause issues
        headers[key.strip().decode()] = value.decode()
    if not host: # TODO: remove this constraint, especially when HTTP2 is supported in the future
        print("Need to specify a Host header!")
        sys.exit(1)

    url = f"{scheme}://{host}{path}"
    return Request(method=method,url=url,headers=headers,body=body,host=host,version=version)

def manual_request(scheme,method,host,url,version,headers,body):
    return Request(method=method,url=url,headers=headers,body=body,host=host,version=version)

def requests_request(request):
    if request.data == []:
        request.data=None
    return Request(method=request.method,url=request.url,headers=request.headers,body=request.data)

class Request:

    def __init__(self, method=None, url=None, headers=None, body=None,host=None,version=None):
        self.sessions=[requests.Session()] # Increase the number of sessions to handle requests in parallel
        self.method = method
        self.url = url
        self.script=None
        if isinstance(headers,dict):
            new_headers = Headers()
            for k,v in headers.items():
                new_headers[k] = v
            headers=new_headers
        self._headers = headers or Headers()
        self._cookies = self._headers.get("cookie")
        self.body = body
        self.host=host or self.url.split("/")[2]
        if version == "HTTP/2": # TODO: remove this constraint when requests gets support for HTTP2
            version = "HTTP/1.1" 
        self.version = version or "HTTP/1.1"

    def copy(self):
        r2 = Request(method=self.method,url=self.url,headers=self.headers,body=self.body,host=self.host,version=self.version)
        r2.sessions=self.sessions
        return r2

    @property
    def headers(self):
        new_headers = Headers()
        for k,v in self._headers._headers.items():
            new_headers._headers[k] = v.copy()
        return new_headers

    @property
    def cookies(self):
        """Parse cookies from the Cookie header."""
        cookie_header = self._headers.get("Cookie", "")
        cookies = {}
        if cookie_header:
            for cookie in cookie_header.split(";"):
                if "=" in cookie:
                    key, value = cookie.strip().split("=", 1)
                    cookies[key] = value
        return cookies


    def __str__(self):
        """String representation of the HTTP request."""
        request_line = f"{self.method} {self.url} HTTP/1.1"
        headers = "\n".join(f"{k}: {v}" for k, v in self._headers.items())
        if headers:
            headers += "\n"
        body = self.body or b""
        return remove_placeholders(f"{request_line}\nHost: {self.host}\n{headers}\n{body.decode()}")

    def send(self, method=None,url=None,headers=None,data=None, insertions=None,debug=False,**kwargs):
        """Send the HTTP request using the requests library."""
        response = None
        error = b""
        current_session=random.choice(self.sessions)
        request = self.copy()
        if insertions is not None:
            for insertion in insertions:
                request = insertion.insert_request(request)

        HTTPConnection._http_vsn_str = request.version # TODO: This will not work great if fuzzing the version string. Please make modifications here whenever HTTP2 support is launched.

        request = remove_placeholders(request) # Removes any custom placeholders in the request
        body = data or request.body
        if not body:
            body = None
        req = requests.Request(
                method=method or request.method,
                url=url or request.url,
                data=body
                )
        prepped=req.prepare()
        prepped.headers = request.headers or self.headers
        if body and prepped.headers.get("Content-Length") is None: # Repairing Content-Length if no custom Content-Length header is set
            prepped.headers = prepped.headers.copy() # Ensuring original headers are untouched
            prepped.headers['Content-Length']= len(body)
        start_time = time.perf_counter()
        try:
            response=current_session.send(prepped,**kwargs)
            response_time = (time.perf_counter() - start_time)*1000
        except Exception as e:
            response_time = (time.perf_counter() - start_time)*1000
            if debug is True:
                print(f"Error occured: {e}")
            error = str(type(e)).encode()

        return response,response_time,error
