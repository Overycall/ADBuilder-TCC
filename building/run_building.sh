#!/bin/bash
[ $1 ] && [ -d $1 ] && [ $2 ] && [ -d $2 ] && [ $3 ] && [ -d $3 ] && [ $4 ] && [ -d $4 ] || { echo "[BUILD] Usage: <path_labelling_queue> <path_building_queue> <path_logs_building>"; exit; }

LABELLING_QUEUE=$1
EXTRACTION_QUEUE=$2
BUILDING_QUEUE=$3
LOG_DIR=$4

[ -d $BUILDING_QUEUE/Clean ] || { mkdir -p $BUILDING_QUEUE/Clean; }
[ -d $BUILDING_QUEUE/Final ] || { mkdir -p $BUILDING_QUEUE/Final; }
[ -d $LOG_DIR ] || { mkdir -p $LOG_DIR; }

TS=$(date +%Y%m%d%H%M%S)
[ -d $LOG_DIR/stats-$TS ] || { mkdir -p $LOG_DIR/stats-$TS; }

[ -f $BUILDING_QUEUE/building.finished ] && { rm $BUILDING_QUEUE/building.finished; }

while [ 1 ]
do
  # checks if there is any .extracted file in the building directory
  for FILE in $(find $BUILDING_QUEUE -type f -name \*.extracted)
  do
    # get apk name without PATH and without extension
    APK_FILENAME=$(basename $FILE .extracted)

    if [ ! -f $BUILDING_QUEUE/Clean/$APK_FILENAME.csv ]
    then
      /usr/bin/time -f "$APK_FILENAME Elapsed Time for CSV Generation = %e seconds, CPU = %P, Memory = %M KiB" \
        -a -o $LOG_DIR/stats-$TS/stats-Geration.log \
        python3 ./building/dataset_geration.py \
        --json $EXTRACTION_QUEUE/extracted/$APK_FILENAME.json \
        --outdir $BUILDING_QUEUE/Clean/ &
    else
      if [ -f $BUILDING_QUEUE/$APK_FILENAME.labeled ] && [ ! -f $BUILDING_QUEUE/Clean/$APK_FILENAME.added ]
      then
        /usr/bin/time -f "$APK_FILENAME Elapsed Time for CSV Concatenation = %e seconds, CPU = %P, Memory = %M KiB" \
          -a -o $LOG_DIR/stats-$TS/stats-Concat.log \
          python3 ./building/dataset_concat.py \
          --incsv $BUILDING_QUEUE/Clean/$APK_FILENAME.csv \
          --inlabeled $LABELLING_QUEUE/labeled/$APK_FILENAME.csv \
          --outdir $BUILDING_QUEUE/Final/ &
        # PID of the concatenation process, for the building to wait for this PID to kill the processes
        PID_CONCAT=$$
        wait
        rm -f $BUILDING_QUEUE/$APK_FILENAME.extracted
        rm -f $BUILDING_QUEUE/$APK_FILENAME.labeled
        touch $BUILDING_QUEUE/Clean/$APK_FILENAME.added
      fi
    fi
  done
  EXTRACTED_COUNT=$(find $EXTRACTION_QUEUE/extracted -type f -name \*.json | wc -l)
  ADDED_COUNT=$(find $BUILDING_QUEUE/Clean -type f -name \*.added | wc -l)

  # check if all CSVs have already been processed
  if [ -f $EXTRACTION_QUEUE/extraction.finished ] && [ -f $LABELLING_QUEUE/labelling.finished ] && [ $EXTRACTED_COUNT -eq $ADDED_COUNT ]
  then
    # wait for current process PID
    wait $PID_CONCAT > /dev/null 2>&1
    touch $BUILDING_QUEUE/building.finished
    exit
  fi
  sleep 5
done
