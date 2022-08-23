#!/bin/bash

set -e

cd /opt/osgconnect-report

. venv/bin/activate

python3 ./generate_user_report.py "$@"

