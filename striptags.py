from types import *

def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def striptags(obj):
    if type(obj) == DictType:
        r = {}
        for key in obj:
            r[key] = striptags(obj[key])
    
    elif type(obj) == ListType:
        r = []
        for item in obj:
            r.append(striptags(item))
            
    elif type(obj) == StringType or type(obj) == UnicodeType:
        r = escape(obj)
    
    else:
        r = obj
    
    return r
