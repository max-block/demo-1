#!/bin/sh

echo 'waiting for mongodb...'
while ! nc -z $DATABASE_HOST 27017; do
  sleep 0.1
done
echo 'mongodb started'

exec "$@"
