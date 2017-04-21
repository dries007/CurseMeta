#!/bin/env python3
"""
CurseMeta

Use output of https://github.com/NikkyAI/alpacka-meta to make static metadata 
used by CurseModpackDownloader v1.x to get all modfiles.

Copyright 2017 Dries007

Licensed under the EUPL, Version 1.1 only (the "Licence");
You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/software/page/eupl5

Unless required by applicable law or agreed to in writing, software
distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing
permissions and limitations under the Licence.
"""
import calendar
import sys
import getopt
import json

from pathlib import Path

import time

from collections import defaultdict


FILE_FILTER_LIST = (
    'Modules', 'CommentCount', 'DownloadCount', 'GamePopularityRank', 'InstallCount', 'Likes', 'PopularityScore',
    'PrimaryCategoryAvatarUrl', 'PrimaryCategoryName', 'Rating')


def filter_file(file):
    for x in FILE_FILTER_LIST:
        if x in file:
            del x


def run(input_folder, output_folder):
    if not input_folder.is_dir():
        raise IOError("Input not a folder.")
    if not output_folder.exists():
        output_folder.mkdir()
    if not output_folder.is_dir():
        raise IOError("Input not a folder.")
    root_content = set()
    for x in input_folder.iterdir():
        # skip .git(ignore) and other hidden files/folders
        if x.name[0] == '.':
            continue
        root_content.add(int(x.stem))
        if x.is_dir():
            # x is project dir
            x_content = defaultdict(list)
            x_out = Path(output_folder, x.name)
            if not x_out.exists():
                x_out.mkdir()
            for y in x.iterdir():
                y_out = Path(x_out, y.name)
                # y is files.json, array of file objects
                if y.name == 'files.json':
                    x_content['files'] = y.name
                    with y.open() as f:
                        data = json.load(f)
                    for file in data:
                        filter_file(file)
                    with y_out.open('w') as f:
                        json.dump(data, f)
                # y is file object
                elif y.suffix == '.json':
                    x_content['ids'].append(int(y.stem))
                    with y.open() as f:
                        data = json.load(f)
                    filter_file(data)
                    with y_out.open('w') as f:
                        json.dump(data, f)
                # y is description.html
                elif y.name == 'description.html':
                    y_out.write_bytes(y.read_bytes())
                    x_content['description'] = y_out.name
                # y is changelog html
                elif y.suffix == '.html':
                    y_out.write_bytes(y.read_bytes())
                # y is unknown, skipped.
                else:
                    print('Skipping unknown file', x.relative_to(input_folder))

            x_content['ids'] = sorted(x_content['ids'])
            Path(x_out, 'index.json').write_text(json.dumps(x_content))
        else:
            # x is file, aka a project json
            with x.open() as f:
                data = json.load(f)
            for file in data['LatestFiles']:
                filter_file(file)
            with Path(output_folder, x.relative_to(input_folder)).open('w') as f:
                json.dump(data, f)
    # @formatter:off
    Path(output_folder, 'index.json').write_text(json.dumps(
        {
            'timestamp': calendar.timegm(time.gmtime()),
            'timestamp_human': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
            'ids': sorted(root_content)
        }))
    # @formatter:on
    print("Did %d projects in total." % len(root_content))


def main(argv):
    input_folder = 'in'
    output_folder = 'out'
    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['help', 'input=', 'output='])
    except getopt.GetoptError:
        print('test.py -i <input_folder> -o <output_folder>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('test.py -i <input_folder> -o <output_folder>')
            sys.exit()
        elif opt in ('-i', '--input'):
            input_folder = arg
        elif opt in ('-o', '--output'):
            output_folder = arg
    print('Input folder is:', input_folder)
    print('Output folder is:', output_folder)

    run(Path(input_folder).resolve(), Path(output_folder).resolve())


if __name__ == '__main__':
    main(sys.argv[1:])
