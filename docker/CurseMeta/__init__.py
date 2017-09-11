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

import calendar
import json
import time

from pathlib import Path


def _filter_latest(x):
    del x['ProjectFileName']
    return x


def parse_top_level_files(file):
    ids = []
    summery = {}

    with file.open(encoding='utf-8') as f:
        data = json.load(f)['Data']

    for project in data:
        ids.append(project['Id'])
        summery[project['Id']] = {
            'Name': project['Name'],
            'PrimaryAuthorName': project['PrimaryAuthorName'],
            'Summary': project['Summary'],
            'WebSiteURL': project['WebSiteURL'],
            'GameVersionLatestFiles': [_filter_latest(x) for x in project['GameVersionLatestFiles']]
        }

    return ids, summery


def _filter_file(file):
    del file['Modules']
    return file


def parse_addon_folder(project_in, project_out, log=True):
    project_files = Path(project_in, 'files')

    if not Path(project_in, 'index.json').exists():
        print("No index, skipping addon folder.")
        return

    if not project_out.is_dir():
        project_out.mkdir(parents=True)

    # make out/<projectid>.json
    with Path(project_in, 'index.json').open(encoding='utf-8') as f:
        project_data = json.load(f)
    for file in project_data['LatestFiles']:
        _filter_file(file)
    with Path(project_out.parent, project_in.name).with_suffix('.json').open('w', encoding='utf-8') as f:
        json.dump(project_data, f, sort_keys=True)

    ids = set()
    # make out/<projectid>/files.json
    with Path(project_files, 'index.json').open(encoding='utf-8') as f:
        data = json.load(f)
    for file in data:
        _filter_file(file)
        ids.add(file['Id'])
    with Path(project_out, 'files.json').open('w', encoding='utf-8') as f:
        json.dump(data, f, sort_keys=True)

    # make out/<projectid>/index.json
    with Path(project_out, 'index.json').open('w', encoding='utf-8') as f:
        json.dump({
            'type': project_data['CategorySection']['Name'],
            'ids': sorted(ids),
            'Name': project_data['Name'],
            'PrimaryAuthorName': project_data['PrimaryAuthorName'],
            'Summary': project_data['Summary'],
        }, f)

    # make out/<projectid>/<fileid>.json
    for file in project_files.iterdir():
        if file.name == 'index.json':
            continue
        with file.open(encoding='utf-8') as f:
            data = json.load(f)
        _filter_file(data)
        data['_Project'] = {
            'Name': project_data['Name'],
            'PrimaryAuthorName': project_data['PrimaryAuthorName'],
            'Summary': project_data['Summary'],
            'PackageType': project_data['CategorySection']['PackageType'],
            'Path': project_data['CategorySection']['Path'],
        }
        with Path(project_out, file.name).open('w', encoding='utf-8') as f:
            json.dump(data, f, sort_keys=True)
    if log:
        print("Done parsing addon", project_in.name)


def run(input_folder, output_folder):
    if not input_folder.is_dir():
        raise IOError('Input not a folder.')
    if not output_folder.is_dir():
        raise IOError('Output not a folder.')

    print('Parsing mods.json ...')
    mod_ids, mods = parse_top_level_files(Path(input_folder, 'mods.json'))
    print('Parsing modpacks.json ...')
    modpack_ids, modpacks = parse_top_level_files(Path(input_folder, 'modpacks.json'))
    all_ids = mod_ids + modpack_ids
    # print('Parsing complete.json ...')
    # all_ids, _ = parse_top_level_files(Path(input_folder, 'complete.json'))
    print('Parsing addons ...')
    for project in Path(input_folder, 'addon').iterdir():
        if project.is_dir():
            parse_addon_folder(project, Path(output_folder, project.name), log=False)

    with Path(output_folder, 'mods.json').open('w', encoding='utf-8') as f:
        json.dump(mods, f, sort_keys=True)

    with Path(output_folder, 'modpacks.json').open('w', encoding='utf-8') as f:
        json.dump(modpacks, f, sort_keys=True)

    with Path(input_folder, 'complete.json').open(encoding='utf-8') as f:
        timestamp = int(json.load(f)['Timestamp']/1000)

    with Path(output_folder, 'index.json').open('w', encoding='utf-8') as f:
        json.dump({
            'timestamp': calendar.timegm(time.gmtime(timestamp)),
            'timestamp_human': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(timestamp)),
            'mods': sorted(mod_ids),
            'modpacks': sorted(modpack_ids),
            'ids': sorted(all_ids),
        }, f)
    print("Done parsing addons")

    from .stats import run as run_stats
    run_stats(Path(input_folder, 'complete.json'), output_folder)


def parse_single_file(i, o):
    with i.open(encoding='utf-8') as f:
        file_data = json.load(f)
    _filter_file(file_data)
    if not o.parent.exists():
        o.parent.mkdir(parents=True)
    with o.open('w', encoding='utf-8') as f:
        json.dump(file_data, f, sort_keys=True)
    print('Done parsing single file', i)
