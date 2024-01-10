#!/bin/bash

# SHA1 is required to submit to HTCondor CEs version < 10 with x509userproxy set; mostly affects CEs in Europe

update-crypto-policies --set DEFAULT:SHA1
