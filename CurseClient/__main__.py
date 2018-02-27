from . import *

import json


def main(*args):
    print('ARGS:')
    print(*args, sep='\n')
    print()
    with open('account.json', 'r') as f:
        account = json.load(f)
        login = Login.LoginClient(account['username'], account['password'])
        login.auth()


if __name__ == '__main__':
    import sys
    main(*sys.argv)
