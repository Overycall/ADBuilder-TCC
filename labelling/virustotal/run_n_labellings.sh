#!/bin/bash
[ $1 ] && [ -f $1 ] && [ $2 ] && [ -d $2 ] && [ $3 ] && [ -d $3 ] && [ $4 ] && [ -d $4 ] || { echo "Usage: $0 <sha256.txt> <API_Keys.txt> <path_queue_labelling> <path_queue_building> <path_logs_labelling> "; exit 1; }

#SHA256_NUMBER=$1
VT_KEYS_FILE=$1
LABELLING_QUEUE=$2
BUILDING_QUEUE=$3
LOG_DIR=$4

# Contador de API Keys
VT_KEYS_NUMBER=$(wc -l $VT_KEYS_FILE | cut -d' ' -f1)

LABELED_DIR=$LABELLING_QUEUE/labeled
# verifica se os diretórios existem, se não cria
[ -d $LABELED_DIR ] || { mkdir -p $LABELED_DIR; }
[ -d $LABELLING_QUEUE/Errors ] || { mkdir -p $LABELLING_QUEUE/Errors; }
[ -f $LABELLING_QUEUE/labelling.finished ] && { rm $LABELLING_QUEUE/labelling.finished; }
[ -d $LOG_DIR ] || { mkdir -p $LOG_DIR; }

VT_KEY_COUNTER=1
LABELED_COUNTER=0
COUNTER=0
TS=$(date +%Y%m%d%H%M%S)

# executar os arquivos de arquivos de entrada
for SHA256_LIST_FILE in $LABELLING_QUEUE/500_VT_*
do
    # se o contador for menor ou igual ao numero de API Keys, pega a API Key
    if [ $VT_KEY_COUNTER -le $VT_KEYS_NUMBER ]
    then
        [ -d $LOG_DIR/stats-$TS-$VT_KEY_COUNTER ] || { mkdir -p $LOG_DIR/stats-$TS-$VT_KEY_COUNTER; }
        # pega linha da API Key
        API_KEY=$(sed -n "${VT_KEY_COUNTER}p" $VT_KEYS_FILE)
        # executa o arquivo run_apk_labelling.sh
        ./labelling/virustotal/run_apk_labelling.sh $SHA256_LIST_FILE $API_KEY $LABELLING_QUEUE $BUILDING_QUEUE $LOG_DIR/stats-$TS-$VT_KEY_COUNTER &> $LOG_DIR/$TS-$VT_KEY_COUNTER.log &
        # incrementa contador de API Keys
        ((VT_KEY_COUNTER++))
        ((COUNTER++))
    fi
done

while [ 1 ]
do
  COUNTER_FINISHED=$(find $LABELLING_QUEUE -type f -name \*.finished | wc -l)
  if [ $COUNTER_FINISHED -eq $COUNTER ]
  then
      kill `ps guaxwww | grep run_apk_labelling.sh | awk '{print $2}'` > /dev/null 2>&1
      touch $LABELLING_QUEUE/labelling.finished
      exit
  else
    sleep 5
  fi
done
