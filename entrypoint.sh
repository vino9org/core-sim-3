#!/bin/bash

cd "$(dirname "$0")"

if [ -f ".env" ]; then
    source .env
    env
fi

if [ "$DATABASE_URL" = "" ]; then
    echo DATABASE_URL not set, aborting.
    exit 1
fi

# migration etc.

WRAPPER=

if [ -f "newrelic.ini" ]; then
    export NEW_RELIC_CONFIG_FILE=$(pwd)/newrelic.ini
    WRAPPER="newrelic-admin run-program "
fi

$WRAPPER hypercorn app:app -b 0.0.0.0:5000 -w ${WORKERS:-1}
