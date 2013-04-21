from types import *

def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def striptags(obj):
    if type(obj) == DictType:
        r = {}
        count = 0
        for key in obj:
            if count >= 500:
                break
            count += 1
            r[key] = striptags(obj[key])
    
    elif type(obj) == ListType:
        r = []
        count = 0
        for item in obj:
            if count >= 500:
                break
            count += 1
            r.append(striptags(item))
            
    elif type(obj) == StringType or type(obj) == UnicodeType:
        r = escape(obj[0:50])
    
    else:
        r = obj
    
    return r
