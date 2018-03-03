from . import CurseClient


def main(*args):
    client: CurseClient = CurseClient.from_file()
    print(client.__doc__)


if __name__ == '__main__':
    import sys
    main(*sys.argv)
