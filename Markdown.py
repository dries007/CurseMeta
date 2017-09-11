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
import sys
import getopt
import markdown

from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
{meta}
<title>{title}</title>
<link rel="stylesheet" href="normalize.css">
<link rel="stylesheet" href="pixyll/fonts.css">
<link rel="stylesheet" href="markdown.css">
</head>
<body>
<div>
{body}
</div>
</body>
</html>
"""


def run(input_folder, output_folder):
    if not input_folder.is_dir():
        raise IOError("Input not a folder.")
    output_folder.mkdir(parents=True, exist_ok=True)
    if not output_folder.is_dir():
        raise IOError("Input not a folder.")

    md = markdown.Markdown(extensions=['markdown.extensions.extra', 'markdown.extensions.meta', 'markdown.extensions.sane_lists', 'markdown.extensions.toc'], extension_configs={}, output_format="html5", tab_length=2)

    for in_file in input_folder.iterdir():
        if not in_file.suffix == ".md":
            continue
        out_file = Path(output_folder, in_file.name).with_suffix(".html")
        print(in_file, '->', out_file)
        body = md.convert(in_file.read_text())
        meta = '\n'.join(['<meta name="{}" content="{}">'.format(k, ' '.join(v)) for k, v in md.Meta.items()])
        html = TEMPLATE.format(meta=meta, title=' '.join(md.Meta['title']), body=body)
        out_file.write_text(html)


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

    print("Markdown script done")


if __name__ == '__main__':
    main(sys.argv[1:])

