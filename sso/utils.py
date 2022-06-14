from urllib.parse import quote
from django.shortcuts import redirect
from django.urls import reverse


def parse_query_params(query:dict, exclude=[], append={}):
    
    data = []
    for i in append:
        if(not (i in exclude)):
            v = quote(append[i]) 
            data.append(f"{i}={v}")

    for i in query:
        if(not (i in exclude)):
            v = quote(query[i])
            data.append(f"{i}={v}")

    if(len(data) == 0):
        return ""
    return "?" + "&".join(data)

def reverse_query(url, request=None, query={}, exclude=[], query_params=None, with_redirect=False):
    if(not request == None):
        for i in request.GET:
            query[i] = request.GET[i]

    if(query_params == None):
        query_params = parse_query_params(query, exclude)

    if(with_redirect):
        return redirect(reverse(url) + query_params)
    else:
        return reverse(url) + query_params