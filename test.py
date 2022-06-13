
import routeros_api as r

if __name__ == "__main__":
    ctx = r.connect(
        host="net.smandak.sch.id",
        username="api-sso",
        password="8spcitcsmandak_",
        use_ssl=True,
        plaintext_login=True
    )

    hotspot = ctx.get_resource('/ip/hotspot/user')
    users = hotspot.get(mac_address="FF:EE:DD:CC:BB:AA")
    if(len(users) == 0):
        hotspot.add(
            name="uuid",
            mac_address="FF:EE:DD:CC:BB:AA",
            limit_uptime="2m",
            limit_bytes_in="300",
            limit_bytes_out="400",
            email="alfian.badrul@smandak.sch.id",
            profile="default",
            address="53.100.142.9"
        )
    else:
        print(users[0]["password"])