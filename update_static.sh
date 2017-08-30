#!/usr/bin/env bash

cp -r static/* www
python3 Markdown.py -i static_md -o www
