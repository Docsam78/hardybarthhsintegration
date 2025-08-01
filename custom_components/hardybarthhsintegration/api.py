import requests

def initialize(ip):
    global _ip
    _ip = ip


def post_json(data: dict):
    url = f"http://{_ip}/api/secc"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    return requests.put(url, json=data, headers=headers)

def set_chargemode(mode):
    return post_json({"salia/chargemode": mode})

def set_pausecharging(pause):
    return post_json({"salia/pausecharging": pause})

def set_current_limit(limit):
    return post_json({"salia/manctrl_limit": str(limit)})

