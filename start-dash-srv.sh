#!/usr/bin/env bash

SRV_PORT="${PORT:=8050}"

service nginx start
uwsgi --ini uwsgi.ini --http :${SRV_PORT}

