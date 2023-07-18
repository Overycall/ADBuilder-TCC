#!/bin/bash

[ -d $1 ] && [ -d $2 ] && [ -d $3 ] && [ -d $4 ] && [ $5 ]|| { echo "Uso: $0 <path_extraction_queue> <path_building_queue> <path_logs> <counter>"; exit; }

DOWNLOAD_QUEUE=$1
EXTRACTION_QUEUE=$2
BUILDING_QUEUE=$3
LOGS_DIR=$4
COUNTER=$5

DOWNLOADED_DIR=$DOWNLOAD_QUEUE/downloaded
EXTRACTED_DIR=$EXTRACTION_QUEUE/extracted

while [ 1 ]
do
  FILE=$(find $EXTRACTION_QUEUE -type f -name \*.downloaded | head -n 1)

  if [ -z $FILE ]
    then
      sleep 2
      continue
  fi
  # get apk name without PATH and without extension
  APK_FILENAME=$(basename $FILE .downloaded)

  if [ -f $EXTRACTED_DIR/$APK_FILENAME.json ]
    then
      continue
  fi

  # get LOCK from APK. if the LOCK already exists, skip to the next APK.
  if { set -C; 2>/dev/null > $EXTRACTION_QUEUE/$APK_FILENAME.lock; }; then
    trap "rm -f $EXTRACTION_QUEUE/$APK_FILENAME.lock" EXIT
  else
    continue # LOCK file already exists. go to next APK.
  fi

  mv $EXTRACTION_QUEUE/$APK_FILENAME.downloaded $EXTRACTION_QUEUE/$APK_FILENAME.extracting

  echo -n "Starting Processing APK File $APK_FILENAME ... "
  # extracts APK features and generates statistics
  /usr/bin/time -f "$APK_FILENAME Extraction Elapsed Time = %e seconds, CPU = %P, Memory = %M KiB" \
    -a -o $LOGS_DIR/stats-extraction-$COUNTER.log python3 extraction/extract_apk_features.py \
    --apk $DOWNLOADED_DIR/$APK_FILENAME.apk --outdir $EXTRACTION_QUEUE --logdir $LOGS_DIR

  if [ -f $EXTRACTION_QUEUE/$APK_FILENAME.json ]
  then
    rm -f $EXTRACTION_QUEUE/$APK_FILENAME.extracting
    rm -f $EXTRACTION_QUEUE/$APK_FILENAME.lock
    # signals the building processes that the JSON has already been processed
    touch $BUILDING_QUEUE/$APK_FILENAME.extracted
    mv $EXTRACTION_QUEUE/$APK_FILENAME.json $EXTRACTED_DIR/
    echo "DONE"
  fi
  sleep 10
done
