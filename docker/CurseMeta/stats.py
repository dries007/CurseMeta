import calendar
import json
import pathlib
import collections
import time


class _Encoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Author:
    def __init__(self):
        self.owner = collections.defaultdict(lambda: [])
        self.member = collections.defaultdict(lambda: [])

    def add_project(self, owner, t, pid):
        (self.owner if owner else self.member)[t].append(pid)


def _do_history(output_folder, timestamp, history_obj):
    if not output_folder.exists():
        output_folder.mkdir()
    with pathlib.Path(output_folder, '{}.json'.format(timestamp)).open('w', encoding='utf-8') as f:
        json.dump(history_obj, f)
    with pathlib.Path(output_folder, 'index.json').open('w', encoding='utf-8') as f:
        json.dump({
            'timestamp': calendar.timegm(time.gmtime(timestamp)),
            'timestamp_human': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(timestamp)),
            'history': sorted(int(x.stem) for x in output_folder.iterdir() if x.stem != 'index' and x.suffix == '.json')
        }, f)


def run(complete, output_folder):
    print("Running stats...")
    with complete.open(encoding='utf-8') as f:
        raw = json.load(f)
        timestamp = int(raw['Timestamp']/1000)
        data = raw['Data']
        del raw

    history_obj = {}

    downloads = collections.defaultdict(lambda: 0)
    project_count = collections.defaultdict(lambda: 0)
    authors = collections.defaultdict(lambda: Author())
    version = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
    projects = {}

    for project in data:
        pid = project['Id']
        t = project['CategorySection']['Name']
        dl = project['DownloadCount']

        projects[pid] = {
            'name': project['Name'],
            'type': t,
            'downloads': dl,
            'score': project['PopularityScore'],
        }

        history_obj[pid] = dl

        project_count[t] += 1
        downloads[t] += dl

        authors[project['PrimaryAuthorName']].add_project(True, t, pid)
        for author in project['Authors']:
            authors[author['Name']].add_project(False, t, pid)

        versions = set(x['GameVesion'] for x in project['GameVersionLatestFiles'])
        for gv in versions:
            version[gv][t] += 1

    with pathlib.Path(output_folder, 'stats.json').open('w', encoding='utf-8') as f:
        json.dump({
            'timestamp': calendar.timegm(time.gmtime(timestamp)),
            'timestamp_human': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(timestamp)),
            'stats': {
                'project_count': project_count,
                'downloads': downloads,
                'version': version,
                'authors': authors,
                'projects': projects,
            }
        }, f, cls=_Encoder)

    _do_history(pathlib.Path(output_folder, 'history'), timestamp, history_obj)

    print("Stats done.")


if __name__ == '__main__':
    import sys
    run(*[pathlib.Path(x) for x in sys.argv[1:]])

