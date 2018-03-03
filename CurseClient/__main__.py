from . import *


def main(*args):
    client: CurseClient = CurseClient.from_file()
    client.debug()
    for k, v in client.service.items():
        print(k, v)


if __name__ == '__main__':
    import sys
    main(*sys.argv)
