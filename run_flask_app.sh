#!/bin/sh

service nginx start
exec uwsgi --ini uwsgi.ini