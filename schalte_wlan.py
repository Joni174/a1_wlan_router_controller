#!/usr/bin/python3

import json
import sys

import requests
import hashlib
import base64


def get_tokens(html):
    def find_in_lines(lines, needle):
        for line in lines:
            if needle in line:
                return line
        return None

    lines = html.split("\n")
    paramline = str(find_in_lines(lines, "csrf_param"))
    tokenline = str(find_in_lines(lines, "csrf_token"))

    offset = paramline.find("content")

    param = paramline[paramline.find("\"", offset) + 1: paramline.find("\"", paramline.find("\"", offset) + 1)]
    token = tokenline[tokenline.find("\"", offset) + 1: tokenline.find("\"", tokenline.find("\"", offset) + 1)]
    return param, token


username = "admin"
password = ""
usage = "usage: python schalte_wlan {ein|aus}"
argv = sys.argv
if len(argv) != 2:
    print(usage)
    exit(1)

ein = [
    "ein",
    "Ein",
    "EIN",
    "on",
    "On",
    "ON"
]

aus = [
    "aus",
    "Aus",
    "AUS",
    "off",
    "Off",
    "OFF"
]

if argv[1] in ein:
    ein_oder_aus = True
elif argv[1] in aus:
    ein_oder_aus = False
else:
    print(usage)
    exit(1)

header1 = {
    "Host": "10.0.0.138",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json;charset=UTF-8",
    "_ResponseFormat": "JSON",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Length": "226",
    "Origin": "http://10.0.0.138",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "http://10.0.0.138/html/index.html"
}

with requests.Session() as session:
    meta = session.get("http://10.0.0.138/html/index.html")

    csrf_param, csrf_token = get_tokens(meta.text)

    hashpassword = hashlib.sha256(
        username.encode() +
        base64.b64encode(
            hashlib.sha256(password.encode()).hexdigest().encode()
        ) +
        csrf_param.encode() +
        csrf_token.encode()).hexdigest()

    d = {
        "csrf":
            {
                "csrf_param": csrf_param,
                "csrf_token": csrf_token
            },
        "data":
            {
                "UserName": username,
                "Password": hashpassword,
                "LoginFlag": 1
            }
    }
    response = session.post("http://10.0.0.138/api/system/user_login", json=d)
    meta = session.get("http://10.0.0.138/html/index.html")
    csrf_param, csrf_token = get_tokens(meta.text)
    basic = {
        "csrf": {
            "csrf_param": csrf_param,
            "csrf_token": csrf_token},
        "action": "BasicSettings",
        "data": {
            "config2g": {
                "ID": "InternetGatewayDevice.X_Config.Wifi.Radio.1.",
                "enable": ein_oder_aus}
        }
    }
    response2 = session.post("http://10.0.0.138/api/ntwk/WlanBasic?showpass=false", json=basic)
# print(response.status_code)
# print(response.headers)
# print(response.content)
# print()
# print(response2.status_code)
# print(response2.headers)
# print(response2.content)

if response2.status_code == 200:
    print("successful transmitted action to router!")
    exit(0)
else:
    print("Could not communicate with Router!")
    exit(1)



