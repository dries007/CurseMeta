#!/usr/bin/env bash
docker run -v /var/run/cursemeta:/var/run/export -v /root/cursemeta/out:/out -d $1
