#!/bin/bash

IDS=(${QUERY_STRING//-/ })
PROJECT_ID="${IDS[0]}"
FILE_ID="${IDS[1]}"

FILE_PATH_1="/data/addon/${PROJECT_ID}/files/${FILE_ID}.json"
FILE_PATH_2="/www/${PROJECT_ID}/${FILE_ID}.json"

echo "Content-type: text/json"
echo ""

if [[ -f $FILE_PATH_2 ]]; then
    cat $FILE_PATH_2
    exit 0
fi

dotnet /alpacka-meta/out/alpacka-meta.dll get -o /out/ --file ${PROJECT_ID}:${FILE_ID} 2>&1 >/dev/null

if [[ -f $FILE_PATH_1 ]]; then
    python3 -m CurseMeta $FILE_PATH_1 $FILE_PATH_2
    if [[ -f $FILE_PATH_2 ]]; then
        cat $FILE_PATH_2
        exit 0
    fi
else
    echo "{ \"error\": true, \"code\": 404, \"message\": \"Not found on backend API\" }"
fi

exit 0
