#!/bin/bash
date
cd
git -C alpacka-meta-files fetch --all
git -C alpacka-meta-files reset --hard origin/master
git -C curseMeta fetch --all
git -C curseMeta reset --hard origin/master
mkdir tmp_out
python3 curseMeta/CurseMeta.py -i alpacka-meta-files -o tmp_out
cp -r curseMeta/static/* tmp_out
rsync -r tmp_out/ www/
rm -r tmp_out
date
