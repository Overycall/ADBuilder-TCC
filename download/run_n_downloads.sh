#!/bin/bash
[ $1 ] && [ $2 ] && [ -d $2 ] && [ $3 ] && [ -d $3 ] && [ $4 ] && [ -d $4 ] || { echo "Usage: $0 <n_parallel_downloads> <path_download_queue> <path_extraction_queue> <path_logs_download>"; exit; }

N_PARALLEL_DOWNLOADS=$1
DOWNLOAD_QUEUE=$2
EXTRACTION_QUEUE=$3
LOG_DIR=$4

DOWNLOADED_DIR=$DOWNLOAD_QUEUE/downloaded
[ -d $DOWNLOADED_DIR ] || { mkdir -p $DOWNLOADED_DIR; }
[ -f $DOWNLOAD_QUEUE/download.finished ] && { rm $DOWNLOAD_QUEUE/download.finished; }
[ -d $LOG_DIR ] || { mkdir -p $LOG_DIR; }

COUNTER=0
TS=$(date +%Y%m%d%H%M%S)

for SHA256_LIST_FILE in $DOWNLOAD_QUEUE/queue_*
do
  [ -d $LOG_DIR/stats-$TS-$COUNTER ] || { mkdir -p $LOG_DIR/stats-$TS-$COUNTER; }
  ./download/run_apk_download.sh $SHA256_LIST_FILE $DOWNLOAD_QUEUE $EXTRACTION_QUEUE $LOG_DIR/stats-$TS-$COUNTER &> $LOG_DIR/$TS-$COUNTER.log &
	((COUNTER++))
done

while [ 1 ]
do
	COUNTER_FINISHED=$(find $DOWNLOAD_QUEUE -type f -name \*.finished | wc -l)
	if [ $COUNTER_FINISHED -eq $COUNTER ]
	then
		kill `ps guaxwww | grep run_apk_download.sh | awk '{print $2}'` > /dev/null 2>&1
    touch $DOWNLOAD_QUEUE/download.finished
		exit
  else
    sleep 5
	fi
done
