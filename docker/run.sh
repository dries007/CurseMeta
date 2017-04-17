#!/bin/bash

spawn-fcgi -s /var/run/export/fcgiwrap.socket /usr/sbin/fcgiwrap
chmod og+rw /var/run/export/fcgiwrap.socket

sleep infinity
