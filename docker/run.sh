#!/usr/bin/env bash

RUN=$1

cd

if [ -f .working_lock ]; then
    echo Was working already: `date`
    exit
fi
touch .working_lock

echo Downloading...
dotnet /alpacka-meta/out/alpacka-meta.dll download -o /data --filter None ${RUN}

echo Python magic...
python3 -m CurseMeta /data /data/www

rm .working_lock
