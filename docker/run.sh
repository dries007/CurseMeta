#!/bin/bash

git clone https://github.com/NikkyAI/alpacka-meta.git
cd alpacka-meta
dotnet restore

spawn-fcgi -s /var/run/export/fcgiwrap.socket /usr/sbin/fcgiwrap
chmod og+rw /var/run/export/fcgiwrap.socket

sleep infinity
