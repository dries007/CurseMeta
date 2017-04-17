#!/bin/bash
# This script is run by cron every 30 minutes, at 15 and 45, to catch the 00 and 50 updates from 'alpacka-meta-files'.
# It is just in the repo for completeness, this file is not actually run.
date
cd
git -C alpacka-meta-files pull
git -C curseMeta pull
mkdir tmp_out
python3 curseMeta/CurseMeta.py -i alpacka-meta-files/addon/ -o tmp_out
cp curseMeta/static/* tmp_out
rsync -r tmp_out/ www/
rm -r tmp_out
date
