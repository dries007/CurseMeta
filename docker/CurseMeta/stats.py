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
        self.owner = collections.defaultdict(lambda: {})
        self.member = collections.defaultdict(lambda: {})

    def add_project(self, owner, t, pid, dl):
        (self.owner if owner else self.member)[t][pid] = dl


def run(complete, output_folder):
    print("Running stats...")
    with complete.open(encoding='utf-8') as f:
        raw = json.load(f)
        timestamp = int(raw['Timestamp']/1000)
        data = raw['Data']
        del raw

    downloads = collections.defaultdict(lambda: 0)
    projects = collections.defaultdict(lambda: 0)
    authors = collections.defaultdict(lambda: Author())
    version = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))

    for project in data:
        pid = project['Id']
        t = project['CategorySection']['Name']
        dl = project['DownloadCount']

        projects[t] += 1
        downloads[t] += dl

        authors[project['PrimaryAuthorName']].add_project(True, t, pid, dl)
        for author in project['Authors']:
            authors[author['Name']].add_project(False, t, pid, dl)

        for gv in project['GameVersionLatestFiles']:
            version[gv['GameVesion']][t] += 1

    with pathlib.Path(output_folder, 'stats.json').open('w', encoding='utf-8') as f:
        json.dump({
            'timestamp': calendar.timegm(time.gmtime(timestamp)),
            'timestamp_human': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(timestamp)),
            'stats': {
                'projects': projects,
                'downloads': downloads,
                'version': version,
                'authors': authors,
            }
        }, f, cls=_Encoder)
    print("Stats done.")


if __name__ == '__main__':
    import sys
    run(*[pathlib.Path(x) for x in sys.argv[1:]])

