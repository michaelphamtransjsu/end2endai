#!/usr/bin/env bash
set -euo pipefail
mkdir -p data/full
kaggle competitions download -c nyc-taxi-trip-duration -p data/full
printf 'Downloaded archive to data/full (excluded from git). Unzip and pass train.csv to the trainer.\n'
