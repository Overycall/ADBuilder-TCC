[ $1 ] &&  [ -f $1 ] && [ $2 ] && [ $3 ] && [ -d $3 ] && [ $4 ] && [ -d $4 ] && [ $5 ] && [ -d $5 ] || { echo "Uso: $0 <sha256.txt> <API_Key> <path_queue_labelling> <path_queue_building> <path_logs_labelling>"; exit;}

SHA256_LIST_FILE=$1
API_KEY=$2
LABELLING_QUEUE=$3
BUILDING_QUEUE=$4
LOG_DIR=$5

SHA256_LIST_FILENAME=$(basename $SHA256_LIST_FILE)
LABELED_DIR=$LABELLING_QUEUE/labeled

# get the last line (sha256) of file
LAST_SHA256=$(tail -n 1 $SHA256_LIST_FILE)

while read SHA256 || [ -n "$SHA256" ]
do
	if [ -f $LABELED_DIR/$SHA256.csv ]
	then
		continue
	fi

	echo -n "Downloading JSON $SHA256 ... "
	echo -e "\nUsed VT API Key: $API_KEY"

	/usr/bin/time -f "$SHA256 Elapsed Time of VT Analysis = %e seconds, CPU = %P, Memory = %M KiB" \
		-a -o $LOG_DIR/stats-"$SHA256_LIST_FILENAME".log \
		python3 labelling/virustotal/label.py \
		--sha256 $SHA256 --vt_key $API_KEY --outdir $LABELLING_QUEUE

	if [ -f $LABELED_DIR/$SHA256.csv ]
	then
		touch $BUILDING_QUEUE/$SHA256.labeled
	fi

	echo -e "Finished $SHA256 Label!!!\n"

	# check if the last APK of the file has already been downloaded
	if [ -f $LABELED_DIR/$LAST_SHA256.csv ] || [ -f $LABELLING_QUEUE/Errors/$LAST_SHA256.json ]
	then
		mv $LABELLING_QUEUE/$SHA256_LIST_FILENAME $LABELLING_QUEUE/$SHA256_LIST_FILENAME.finished
	else
		# wait for new request
		sleep 20
	fi
done < $SHA256_LIST_FILE
