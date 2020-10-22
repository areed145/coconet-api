from datetime import datetime, timezone
from clint.textui import colored
from pyfiglet import figlet_format


def meta():
    info = {}
    info["title"] = "Coconet"
    info["description"] = "API supporting kk6gpv.net"
    info["version"] = "v0.1"
    info["author"] = "Adam Reeder, KK6GPV"
    info["date"] = datetime.now(timezone.utc)
    info["copyright"] = 2020

    print(figlet_format(info["title"] + " " + info["version"], font="slant"))
    for key in info:
        print(colored.green(key + ":"), info[key])

    return info
