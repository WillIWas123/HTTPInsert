# HTTPInsert

A library written for finding insertion points in HTTP requests and injecting palyoads.

- [Disclaimer](https://github.com/WillIWas123/HTTPInsert#disclaimer)
- [About](https://github.com/WillIWas123/HTTPInsert#about)
- [Installation](https://github.com/WillIWas123/HTTPInsert#installation)
- [Example usage](https://github.com/WillIWas123/HTTPInsert#example-usage)
- [Custom insertion points](https://github.com/WillIWas123/HTTPInsert#custom-insertion-points)
- [Todo](https://github.com/WillIWas123/HTTPInsert#todo)


## Disclaimer

- This is considered to be a beta release, and may contain bugs and unintentional behavior. Consider yourself warned!

## About

[HTTPInsert](https://github.com/WillIWas123/HTTPInsert) is a library written for finding insertion points in HTTP requests and injecting palyoads. 


There are countless scanners parsing for insertion points in their own unique way, some better than others. This is my attempt at making a simple to use library for finding and handling insertion points, making it easier to create new and awesome vulnerabilitiy scanners. 


## Installation

```python3 -m pip install httpinsert```


## Example usage

```python
from httpinsert import Location, requests_request
from httpinsert.insertion_points import InsertionPoint, find_insertion_points
from requests import Request

requests_req = Request("GET","https://example.com/endpoint?param=value&other=param")

httpinsert_request = requests_request(requests_req)

insertion_points = find_insertion_points(httpinsert_request,default=True,location="Query") # Specifying default=True excludes multiple params such as keys

payload = "SomePayloadToInject"
for insertion_point in insertion_points:
    insertion = insertion_point.insert(payload,httpinsert_request,format_payload=True)
    resp, response_time, error = httpinsert_request.send(insertions=[insertion])
    print(resp,response_time,error,insertion.full_section) # full_section is the full section after the payload is injected. In this case full_section is the full URL.
    print(insertion.full_section == resp.request.url) # True

```



## Custom insertion points

It is possible to create custom logic for finding insertion points and injecting payloads.


Here's an example of how to create a new insertion point between all dashes:

```python
class Dashes(Location):
    def find_insertion_points(self,request):
        parsed_url = urlparse(request.url)
        path = parsed_url.path
        segments = path.split("-")
        insertion_points = []
        for c,segment in enumerate(segments):
            insertion_points.append(InsertionPoint(self,"dashes", str(c), segment))
        return insertion_points

    def insert_payload(self,request,insertion_point,payload,default_encoding):
        if default_encoding is True:
            if isinstance(payload,str):
                payload=quote(payload) # Encode the payload
            else:
                payload = [quote(i) for i in payload]
        parsed_url = urlparse(request.url)
        path = parsed_url.path
        segments = path.split("-")
        if int(insertion_point.key) == len(segments):
            path+=payload
        else:
            segments[int(insertion_point.key)] = payload
            path = "-".join(segments)
        url = urlunparse(parsed_url._replace(path=path))
        request.url=url
        return request,request.url

Dashes() # Important to create the object to include this object in the list of custom insertion points
```

## Todo

- Properly handle errors
- Add more content types such as multipart
- Add support of converting between content types
- Multiple TODO's are scattered around the code, these will be addressed some time in the future.
- Consider writing a custom JSON parsing library
- Consider writing a cusom XML parsing library
