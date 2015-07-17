#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "usage:"
    echo
    echo "    $ ./upload-bot.sh <dir>"
    echo
    echo "Upload a bot located at <dir> to botfights."
    echo "On success, your bot_id will be returned. Use this id"
    echo "to register your bot for a fight."
    echo
    echo "See http://botfights.io/ for more documentation."
    exit 1
fi

DIR=$1
TMPFILE=$(mktemp -t "XXXXXXXXXX")
echo "# tar'ing up ${DIR} ..."
pushd ${DIR} > /dev/null
tar czf ${TMPFILE} ./ > /dev/null
popd > /dev/null
ID=`shasum $TMPFILE | cut -c1-40`
echo "# sha is: ${ID}"
echo "# PUT'ing tarball to drop.botfights.io ..."
curl -X PUT --data-binary @$TMPFILE http://drop.botfights.io/bot/$ID
echo "# success! wait a couple minutes, then check the following for status:"
echo "# http://s3.botfights.io/bot/${ID}/metadata.json"
echo $ID

