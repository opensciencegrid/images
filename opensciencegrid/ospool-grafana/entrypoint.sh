#!/bin/bash
set -euo pipefail

# get our dashboards from git
cd /tmp
git clone https://github.com/osg-htc/ospool-display.git
cp -r ospool-display/grafana/provisioning/* /etc/grafana/provisioning/
mkdir -p /var/lib/grafana/dashboards
cp ospool-display/grafana/dashboards/* /var/lib/grafana/dashboards/

# back to Grafana's own entrypoint
exec /run.sh "$@"

