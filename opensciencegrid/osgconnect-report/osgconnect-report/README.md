# User Account Reporting Tool

This user account reporting tool has been developed to automate the process of
reporting the number of weekly new account requests and new accounts accepted
through OSG Connect. 

To accomplish this, the script `generate_user_report.py` pulls user information
from the OSG Connect User Database, saves a snapshot of the database (only 
information needed to generate the report is saved), and compares it to a 
previously saved snapshot in order to count the metrics previously mentioned.

`generate_user_report.py` will send an HTML email report to the given recipients
upon completion. 

## Prerequisites

1. a file in the current working directory called `osgconnect.token` with a 
    token that has access to use the OSG User Account Database REST endpoint
1. a file in the current working directory called `mailgun.token` with a 
    token that has access to use the ci-connect mailgun

## Usage

```
usage: generate_user_report.py [-h] [--recipients RECIPIENTS [RECIPIENTS ...]] [--start START] [--end END] [--debug]

Collects user account metrics, generates an html report, and sends it to the given recipients.

optional arguments:
  -h, --help            show this help message and exit
  --recipients RECIPIENTS [RECIPIENTS ...]
                        recipients to which the report will be sent
  --start START         snapshot to start from, used to 'replay' from a specific snapshot
  --end END             snapshot to end with, used to 'replay' from a specific snapshot
  --debug               enable debug mode
```

Example: `python3 generate_user_report.py --recipients email@domain`

