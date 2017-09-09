import json


def _decode_hook(d):
    if 'Modules' in d:
        del d['Modules']
    return d


def run(raw_file):
    with open(raw_file) as f:
        raw = json.load(f, object_hook=_decode_hook)

    with open('tmp.json', 'w') as f:
        json.dump(raw, f, indent=2)


if __name__ == '__main__':
    import sys
    run(*sys.argv[1:])
