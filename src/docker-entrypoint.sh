#!/bin/sh

flask db init
flask db migrate
flask db upgrade
# psql -U XXX -d XXX -f /docker-entrypoint-initdb.d/10-init.sql -h db
python server.py