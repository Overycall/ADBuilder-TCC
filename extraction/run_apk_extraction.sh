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
  # pega nome do APK sem PATH e sem extensao
  APK_FILENAME=$(basename $FILE .downloaded)

  if [ -f $EXTRACTED_DIR/$APK_FILENAME.json ]
    then
      continue
  fi

  # pega o LOCK do APK. se o LOCK ja existir, pula para o proximo APK.
  if { set -C; 2>/dev/null > $EXTRACTION_QUEUE/$APK_FILENAME.lock; }; then
    trap "rm -f $EXTRACTION_QUEUE/$APK_FILENAME.lock" EXIT
  else
    continue # arquivo de LOCK ja existe. vai para proximo APK.
  fi

  mv $EXTRACTION_QUEUE/$APK_FILENAME.downloaded $EXTRACTION_QUEUE/$APK_FILENAME.extracting

  echo -n "Starting Processing APK File $APK_FILENAME ... "
  # extrai as caracteristicas do APK e gera estatisticas
  /usr/bin/time -f "$APK_FILENAME Extraction Elapsed Time = %e seconds, CPU = %P, Memory = %M KiB" \
    -a -o $LOGS_DIR/stats-extraction-$COUNTER.log python3 extraction/extract_apk_features.py \
    --apk $DOWNLOADED_DIR/$APK_FILENAME.apk --outdir $EXTRACTION_QUEUE --logdir $LOGS_DIR

  if [ -f $EXTRACTION_QUEUE/$APK_FILENAME.json ]
  then
    rm -f $EXTRACTION_QUEUE/$APK_FILENAME.extracting
    rm -f $EXTRACTION_QUEUE/$APK_FILENAME.lock
    # sinaliza os processos de building que o CSV ja foi todo gravado
    touch $BUILDING_QUEUE/$APK_FILENAME.extracted
    mv $EXTRACTION_QUEUE/$APK_FILENAME.json $EXTRACTED_DIR/
    echo "DONE"
  fi
  sleep 10
done
