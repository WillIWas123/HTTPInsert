from collections import OrderedDict

class Headers:
    def __init__(self,data=None):
        self._headers = OrderedDict()
        if data is not None:
            self._headers=data

    def __getitem__(self,key):
        if self._headers.get(key):
            return ", ".join(self._headers[key])

    def __setitem__(self,key,value):
        if self._headers.get(key) is None:
            self._headers[key] = []
        if isinstance(value,str):
            self._headers[key].append(value)
        elif isinstance(value,list):
            self._headers[key] = value

    def __iter__(self):
        for k in self._headers:
            yield k

    def __delitem__(self,key):
        del self._headers[key]

    def __repr__(self):
        o = ""
        for k,v in self.items():
            o+=f"{k}: {v}\n"
        return o

    def values(self):
        out=[]
        for i in self._headers.values():
            out.append(i)
        return out
    
    def keys(self):
        out = []
        for i in self._headers.keys():
            out.append(i)
        return out

    def get(self,key,default=None):
        if self._headers.get(key):
            return ", ".join(self._headers[key]) # Returns a comma separated list of values for the specified key
        return default

    def pop(self,key,default=None):
        if key not in list(self._headers.keys()):
            return default
        v = self._headers.get(key)
        output=v[0]
        if len(v) == 1:
            del self._headers[key]
        self._headers[key] = v[1:]
        return output

    def items(self):
        for i in self._headers:
            for j in self._headers[i]:
                yield i,j

    def copy(self):
        h2 = Headers()
        for k,v in self.items():
            h2[k] = v
        return h2

    def update(self,test):
        if not test:
            return
        raise NotImplementedError("The update function has not been implemented")
