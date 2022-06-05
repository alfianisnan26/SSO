from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.shortcuts import redirect, render as html_render
import os   
import urllib.parse
class Str:
    langdir = os.path.join(settings.BASE_DIR, "sso", "lang", "langfiles")
    def getLocale():
        dirs = os.listdir(Str.langdir)
        
        a_dirs = []
        for dir in dirs:
            if(".lang" in dir and not "global" in dir):
                a_dirs.append(dir[:-5])
                
        return a_dirs
    
    def loadLocale(self):
        objs1 = open(os.path.join(Str.langdir, f"{self.id}.lang"),"r", encoding='utf8').read().splitlines()
        objs2 = open(os.path.join(Str.langdir, f"global.lang"),"r", encoding='utf8').read().splitlines()
        data = {}
        for obj in objs1 + objs2:
            split = obj.split("=")
            try:
                data[split[0]]
            except:
                data[split[0]] = "=".join(split[1:])
        data["-"] = ""
        self.data = data
    
    def __init__(self, request:HttpRequest = None, id = None):
        try:
            self.request = request
            self.id = request.COOKIES["lang"]
        except:
            self.id = id
            
        locale = Str.getLocale()
        
        if(not self.id in locale):
            self.id = locale[0]
            
        self.loadLocale()

    def get(self, val:str, out="<{}:{}>"):
        if(out == None):
            out = ""
        if(val == None):
            return out.format(val, self.id)
        try:
            return self.data[val]
        except:
            return out.format(val, self.id)
    
    def setLang(self, response:HttpResponse):
        return response
    
    def translateContext(self, context:dict = {}):
        for ctx in context.keys():
            try:
                if("str:" in context[ctx]):
                    context[ctx] = self.get(context[ctx][4:])
                elif(isinstance(context[ctx], dict)):
                    context[ctx] = self.translateContext(context[ctx])
                elif(isinstance(context[ctx], list)):
                    data = []
                    for dt in context[ctx]:
                        data.append(self.translateContext(dt))
                    context[ctx] = data
            except:
                context[ctx] = ""
        
        return context
    
    def setContext(self, context:dict = {}):
        context = self.translateContext(context)
        context["str"] = self.data
        if(not hasattr(context, "referer")):
            context["referer"] = self.request.build_absolute_uri()
        if(not hasattr(context, "next")):
            try:
                context["next"] = urllib.parse.quote(self.request.GET["next"])
            except:
                pass
        langs = []
        for lang in Str.getLocale():
            langs.append({"id":self.get(f"{lang}_id")
            ,"name":self.get(f"{lang}_name")})
        context["langs"] = langs
        return context
    
    def render(self, template_name:str, context = {}, request = None):
        out = html_render(request, template_name=template_name, context=self.setContext(context))
        resp = self.setLang(out)
        return resp
    
    def urlSetLang(request:HttpRequest, lang):
        for i in sorted(request.META):
            print(i, request.META[i], sep=" : ")
        try:
            ret = redirect(request.GET["next"])
        except:
            ret = redirect('home')
        ret.set_cookie('lang', lang)
        return ret