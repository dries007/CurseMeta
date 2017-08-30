#!/usr/bin/env bash

cp -r static/* data/www
python3 Markdown.py -i static_md -o data/www
