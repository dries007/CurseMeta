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

echo "getinfo.sh request to $QUERY_STRING, parsed as $PROJECT_ID $FILE_ID" >>/var/log/getinfo.log 2>>/var/log/getinfo.error

echo "Content-type: text/json"
echo ""

curl https://cursemeta.nikky.moe/api/addon/${PROJECT_ID}/files/${FILE_ID}

exit 0

dotnet /alpacka-meta/out/alpacka-meta.dll get -o /data --filter None --project ${PROJECT_ID} >>/var/log/getinfo.log 2>>/var/log/getinfo.error
dotnet /alpacka-meta/out/alpacka-meta.dll get -o /data --filter None --file ${PROJECT_ID}-${FILE_ID} >>/var/log/getinfo.log 2>>/var/log/getinfo.error

if [[ -f $FILE_PATH_INDEX ]]; then
    python3 -m CurseMeta project $PROJECT_PATH_1 $PROJECT_PATH_2 >>/var/log/getinfo.log 2>>/var/log/getinfo.error
fi

if [[ ! -f $FILE_PATH_2 ]]; then
    python3 -m CurseMeta file $FILE_PATH_1 $FILE_PATH_2 >>/var/log/getinfo.log 2>>/var/log/getinfo.error
fi

if [[ -f $FILE_PATH_2 ]]; then
    cat $FILE_PATH_2
     echo "getinfo $QUERY_STRING OK" >>/var/log/getinfo.log 2>>/var/log/getinfo.error
    exit 0
else
    echo "getinfo $QUERY_STRING ERROR" >>/var/log/getinfo.log 2>>/var/log/getinfo.error
    echo "{ \"error\": true, \"code\": 404, \"message\": \"Not found on backend API\" }"
fi

exit 0
