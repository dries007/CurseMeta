#!/usr/bin/env bash
docker run -v /var/run/cursemeta:/var/run/export -v /root/cursemeta/out:/alpacka.meta -d $1
