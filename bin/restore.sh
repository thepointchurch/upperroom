#!/bin/sh

PROJECT=$( cd $(dirname $0)/.. ; pwd -P )

cd "${PROJECT}" && envdir .env make restore
