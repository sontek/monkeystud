#!/bin/bash

if [[ $# -lt 3 ]]; then
    echo "usage:"
    echo
    echo "    $ ./upload-bot.sh <directory> <game> <branch> [<id>]"
    echo
    echo "where directory is the path of your bot, game and branch are"
    echo "the game and branch of the github.com/botfights repo,"
    echo "and <id> is the identifier of your bot. Leave <id> blank the"
    echo "first time you register your bot, a new id will be generated."
    echo
    echo "See http://botfights.io/ for more documentation."
    exit 1
fi

DIR=$1
GAME=$2
BRANCH=$3
TMPFILE=$(mktemp -t "XXXXXXXXXX")
pushd $DIR;tar czvf $TMPFILE ./;popd
VERSION=`shasum $TMPFILE | cut -c1-40`
ID=$VERSION
if [[ $# -eq 4 ]]; then
    ID=$4
fi
curl -X PUT --data-binary @$TMPFILE http://drop.botfights.io/bot/$GAME/$BRANCH/$ID/$VERSION

echo "Success, your bot id is: $ID"
echo
echo "Write that down; you will need it to update your bot."
echo
echo "Wait a couple minutes then check:"
echo
echo "http://s3.botfights.io/bot/${GAME}/${BRANCH}/${ID}/metadata.json"
echo
echo "Fight!"

