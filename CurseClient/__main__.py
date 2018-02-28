from . import *

import json


def main(*args):
    client = CurseClient.from_file()
    client.debug()


if __name__ == '__main__':
    import sys
    main(*sys.argv)
