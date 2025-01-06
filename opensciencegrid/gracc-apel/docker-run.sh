#!/bin/bash
set -e

echo Generating APEL report...
wrote=$(/usr/libexec/apel/apel_report.py "$@")
echo "$wrote"
apelfile=${wrote#wrote: }

# Output the content of the apelfile before uploading, for debugging purposes
cat "$apelfile"

cp "$apelfile" /var/spool/apel/outgoing/12345678/1234567890abcd

exec ssmsend
