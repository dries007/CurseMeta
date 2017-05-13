#!/bin/bash
echo "Start at `date`"
cd
echo "Updating CurseMeta..."
git -C curseMeta fetch --all
git -C curseMeta reset --hard origin/master
echo "Updating alpacka-meta-files..."
git -C alpacka-meta-files fetch --all
git -C alpacka-meta-files reset --hard origin/master
mkdir tmp_out
python3 curseMeta/CurseMeta.py -i alpacka-meta-files -o tmp_out
python3 curseMeta/Markdown.py -i curseMeta/static_md -o tmp_out
cp -r curseMeta/static/* tmp_out
echo "Syncing to web dir..."
rsync -r --delete tmp_out/ www/
rm -r tmp_out
echo "End at `date`"
