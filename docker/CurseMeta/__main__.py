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

functions = {'file': parse_single_file, 'project': parse_addon_folder, 'all': run}


def main(argv):
    if len(argv) != 3:
        raise Exception("You need 3 args: mode (file, project, or all), in, and out.")
    m = argv[0]
    if m not in functions.keys():
        raise Exception("Mode is not file, project or all.")
    i = Path(argv[1])
    o = Path(argv[2])

    functions[m](i, o)


if __name__ == '__main__':
    main(sys.argv[1:])
