#!/bin/bash

SITEROOT=$1

echo Move to $SITEROOT

cp -r web $SITEROOT
python3 createindex.py > $SITEROOT/index.html
python3 createindex-id.py 6 > $SITEROOT/edo.html
python3 createindex-id.py 8 > $SITEROOT/socnet.html
echo Done
