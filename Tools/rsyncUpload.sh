#!/bin/bash

# This needs to live in /usr/local/bin with an associated serfice file definition
# Check the /home/noaa_gms/RFSS/README.md on specifics 
# Once a service is created, rsync will watch "WATCHED_FOLDER" and when something is dropped in there
# from main python script, then files will be rsynced to EC2
# Also ensure you have rights to write to /tmp for LOCKFILE
LOCKFILE="/tmp/lockfile"
WATCHED_FOLDER="/home/noaa_gms/RFSS/preUpload/"
REMOTE_FOLDER="Administrator@noaa-gms-ec2:/home/Administrator/RFSS"
LOGFILE="/home/noaa_gms/RFSS/rsync.log"

inotifywait -m -r -e modify,move,create,delete --format '%w%f' "${WATCHED_FOLDER}" | while read FILE

do
  if [ ! -e "${LOCKFILE}" ]; then
    touch "${LOCKFILE}"

    # rsync -avc --remove-source-files --rsync-path='c:/cygwin64/bin/rsync' --progress $WATCHED_FOLDER $REMOTE_FOLDER >    # Removed verbose and --progress in  rsync
    rsync -ac --remove-source-files --rsync-path='c:/cygwin64/bin/rsync' $WATCHED_FOLDER $REMOTE_FOLDER >> $LOGFILE

    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    FILENAME=$(basename "$FILE")

    echo "$TIMESTAMP $FILENAME SENT" >> $LOGFILE
    # echo "File(s) uploaded: $FILE" >> $LOGFILE

    rm -f "${LOCKFILE}"
  else
    echo "Previous rsync is still running."
  fi
done