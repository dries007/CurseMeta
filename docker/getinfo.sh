#!/bin/bash

IDS=(${QUERY_STRING//-/ })
PROJECT_ID="${IDS[0]}"
FILE_ID="${IDS[1]}"

FILE_PATH="/data/addon/${PROJECT_ID}/files/${FILE_ID}.json"

echo "Content-type: text/json"
echo ""

if [[ -f $FILE_PATH ]]; then
    cat $FILE_PATH
    exit 0
fi

dotnet /alpacka-meta/out/alpacka-meta.dll get -o /out/ --file ${PROJECT_ID}:${FILE_ID} 2>&1 >/dev/null

if [[ -f $FILE_PATH ]]; then
    python3 -m CurseMeta $FILE_PATH
    cat $FILE_PATH
    exit 0
else
    echo "{ \"error\": true, \"code\": 404, \"message\": \"Not found on backend API\" }"
fi

exit 0
