"""
CurseMeta

Use output of https://github.com/NikkyAI/alpacka-meta to make static metadata
used by CurseModpackDownloader v1.x to get all modfiles.

Copyright 2017 Dries007

Licensed under the EUPL, Version 1.1 only (the 'Licence');
You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/software/page/eupl5

Unless required by applicable law or agreed to in writing, software
distributed under the Licence is distributed on an 'AS IS' basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing
permissions and limitations under the Licence.
"""
import sys

from . import *


def main(argv):
    if len(argv) != 2:
        raise Exception("You need 2 args: in and out.")
    i = Path(argv[0])
    o = Path(argv[1])

    print(i, o)

    if i.is_file():
        print("Single file")
        parse_single_file(i, o)
    else:
        print("Folder")
        run(i, o)


if __name__ == '__main__':
    main(sys.argv[1:])
