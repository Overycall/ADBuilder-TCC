#!/bin/bash

[ $1 ] && [ $2 ] && [ -d $2 ] && [ $3 ] && [ -d $3 ] && [ $4 ] && [ -d $4 ] && [ $5 ] && [ -d $5 ] || { echo "Usage: $0 <n_parallel_extractions> <path_download_queue> <path_extraction_queue> <path_building_queue> <path_logs>"; exit; }

N_PARALLEL_EXTRACTORS=$1
DOWNLOAD_QUEUE=$2
EXTRACTION_QUEUE=$3
BUILDING_QUEUE=$4
LOG_DIR=$5

EXTRACTED_DIR=$EXTRACTION_QUEUE/extracted
[ -d $EXTRACTED_DIR ] || { mkdir -p $EXTRACTED_DIR; }
[ -d $LOG_DIR ] || { mkdir -p $LOG_DIR; }
[ -f $EXTRACTION_QUEUE/extraction.finished ] && { rm $EXTRACTION_QUEUE/extraction.finished; }

COUNTER=1
TS=$(date +%Y%m%d%H%M%S)

for NEXT in $(seq 1 $N_PARALLEL_EXTRACTORS)
do
    [ -d $LOG_DIR/stats-$TS-$COUNTER ] || { mkdir -p $LOG_DIR/stats-$TS-$COUNTER; }
    bash -x ./extraction/run_apk_extraction.sh $DOWNLOAD_QUEUE $EXTRACTION_QUEUE $BUILDING_QUEUE $LOG_DIR/stats-$TS-$COUNTER $COUNTER &> $LOG_DIR/extraction-$TS-$COUNTER.log &
    ((COUNTER++))
done

while [ 1 ]
do
    # counting .downloaded and .extracted files
    EXT_DOWNLOAD=$(find $DOWNLOAD_QUEUE/downloaded -type f -name \*.apk | wc -l)
    EXT_COUNT=$(find $EXTRACTION_QUEUE/extracted -type f -name \*.json | wc -l)

    # check if the download is finished
    if [ -f $DOWNLOAD_QUEUE/download.finished ] && [ $EXT_DOWNLOAD -eq $EXT_COUNT ]
    then
        touch $EXTRACTION_QUEUE/extraction.finished
        kill `ps guaxwww | grep run_apk_extraction.sh | awk '{print $2}'` > /dev/null 2>&1
        exit
    else
      sleep 5
    fi
done
