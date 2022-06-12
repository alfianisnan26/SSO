import ipaddress

from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import redirect

from sso.api.net.models import Registrant

class Network:

    def __init__(self, request:HttpRequest) -> None:
        self.request = request

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        else:
            return self.request.META.get('REMOTE_ADDR')

    def is_coming_from_our_network(self):
        ip = ipaddress.IPv4Address(Network.get_client_ip(self.request))
        net = ipaddress.IPv4Network(settings.ROUTEROS_NETWORK)
        return ip in net


    def connect(self) -> bool:
        q = self.request.GET
        if(self.is_coming_from_our_network()):
            fr = q.get("from")
            if(fr == "login"):
                # IT IS NEED TO LOGIN
                try:
                    reg = Registrant.objects.get(mac=q.get("mac"))
                except:
                    reg = Registrant(
                        mac=q.get("mac"),
                        ip=q.get("ip"),
                        user=self.request.user
                    )

                reg.login()

                return redirect(settings.ROUTEROS_HOST + f"/login/?token={reg.token}&uuid={reg.uuid}")
            elif(fr == "status"):
                # IT HAS LOGIN
                return True
            else:
                # UNKNOWN NEED TO CHECK STATUS
                return redirect()
                pass
        else:
            return False