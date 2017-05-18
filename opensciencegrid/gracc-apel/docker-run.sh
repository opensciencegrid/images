#!/bin/bash

wrote=$(./apel_report.py)
apelfile=${wrote#wrote: }

cp "$apelfile" /var/spool/apel/outgoing/12345678/1234567890abcd

ssmsend

