#!/bin/bash

IDS=(${QUERY_STRING//-/ })
PROJECT_ID="${IDS[0]}"
FILE_ID="${IDS[1]}"

# in:
PROJECT_PATH_1="/data/addon/${PROJECT_ID}"
FILE_PATH_1="${PROJECT_PATH_1}/files/${FILE_ID}.json"
FILE_PATH_INDEX="${PROJECT_PATH_1}/files/index.json"

# out:
PROJECT_PATH_2="/www/${PROJECT_ID}"
FILE_PATH_2="${PROJECT_PATH_2}/${FILE_ID}.json"

echo "getinfo.sh request to $QUERY_STRING, parsed as $PROJECT_ID $FILE_ID" >> /var/log/cron.log

echo "Content-type: text/json"
echo ""

dotnet /alpacka-meta/out/alpacka-meta.dll get -o /data --filter None --project ${PROJECT_ID} 2>&1  >> /var/log/cron.log
dotnet /alpacka-meta/out/alpacka-meta.dll get -o /data --filter None --file ${PROJECT_ID}-${FILE_ID} 2>&1  >> /var/log/cron.log

if [[ -f $FILE_PATH_INDEX ]]; then
    python3 -m CurseMeta project $PROJECT_PATH_1 $PROJECT_PATH_2 2>&1 >> /var/log/cron.log
fi

if [[ ! -f $FILE_PATH_2 ]]; then
    python3 -m CurseMeta file $FILE_PATH_1 $FILE_PATH_2 2>&1 >> /var/log/cron.log
fi

if [[ -f $FILE_PATH_2 ]]; then
    cat $FILE_PATH_2
     echo "getinfo $QUERY_STRING OK" >> /var/log/cron.log
    exit 0
else
    echo "getinfo $QUERY_STRING ERROR" >> /var/log/cron.log
    echo "{ \"error\": true, \"code\": 404, \"message\": \"Not found on backend API\" }"
fi

exit 0
