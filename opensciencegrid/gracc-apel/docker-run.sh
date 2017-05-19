#!/bin/bash
set -e

echo Generating APEL report...
wrote=$(/usr/libexec/apel/apel_report.py)
echo "$wrote"
apelfile=${wrote#wrote: }

cp "$apelfile" /var/spool/apel/outgoing/12345678/1234567890abcd

exec ssmsend
