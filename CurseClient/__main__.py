"""
Test application for the CurseClient package.
"""

import redis
import requests

from . import LoginClient


def main(*param):
    print(*param)
    with open('curse.txt') as f:
        code = f.read().strip()
    print("Curse code", code)
    client = LoginClient(code, redis.Redis.from_url("unix:///run/redis/redis.sock?db=0"))
    print(client)
    print(requests.get("https://addons-v2.forgesvc.net/api/addon/timestamp", headers=client.get_headers()).text)


if __name__ == '__main__':
    import sys
    main(*sys.argv)
