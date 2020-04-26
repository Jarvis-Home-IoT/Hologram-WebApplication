#!/bin/bash

echo "=============================== BEGIN ===============================" >&2

### Variables ###
echo "PYTHON_VERSION=$PYTHON_VERSION" >&2
echo "EXTRAS=$EXTRAS" >&2
echo "S3_BASE=$S3_BASE" >&2
echo "ARCHIVE_NAME=$ARCHIVE_NAME" >&2


### Definitions ###
function terminate {
  echo 'Terminating' >&2
  shutdown -h now
}
trap terminate EXIT

pipcmd="python$PYTHON_VERSION -m pip"
wheeldir="wheels"


### Install dependencies ###
yum -y groupinstall "Development tools"
yum -y install "python${PYTHON_VERSION}-devel"
if [ -n "$EXTRAS" ]
then
  yum -y install $EXTRAS
fi
$pipcmd install wheel


### Fetch archive ###
aws s3 cp "$S3_BASE/$ARCHIVE_NAME" .


### Perform build ###
mkdir "$wheeldir"
$pipcmd wheel -w "$wheeldir" "$ARCHIVE_NAME"


### Upload wheels ###
cd "$wheeldir"
aws s3 cp --recursive . "$S3_BASE"

echo "================================ END ================================" >&2
