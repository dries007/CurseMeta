#!/usr/bin/env bash

RUN=$1

cd

if [ "$RUN" == "Complete" ]; then
    echo Skipping complete
    exit
fi

if [ -f .working_lock ]; then
    echo Was working already: `date`
    exit
fi
touch .working_lock

dotnet /alpacka-meta/out/alpacka-meta.dll download -o /data --filter None ${RUN}

python3 -m CurseMeta /data

rm .working_lock
