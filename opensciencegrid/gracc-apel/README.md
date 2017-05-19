
GRACC to APEL Synchronization
=============================

The scripts in this repository synchronize the accounting data for WLCG sites
in GRACC with the WLCG APEL instance.

For convenience, the latest version of this script is also posted on DockerHub.

Scripts of note:
- `apel_report.py`: Generates a summary of the month's accounting data.
- `docker-run.sh`: Runs the APEL reporting, then sends it to APEL via SSM.

