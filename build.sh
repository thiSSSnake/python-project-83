#!/usr/bin/env sh
make install && psql -a -d $DATABASE_URL -f database.sql