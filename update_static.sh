#!/usr/bin/env bash

mkdir -p data/www
cp -r static/* data/www
python3 Markdown.py -i static_md -o data/www
