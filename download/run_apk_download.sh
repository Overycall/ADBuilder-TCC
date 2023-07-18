[ $1 ] && [ -f $1 ] && [ $2 ] && [ -d $2 ] && [ $3 ] && [ -d $3 ] && [ $4 ] && [ -d $4 ] || { echo "Usage: $0 <APK_SHA256_list.txt> <path_download_queue> <path_extraction_queue> <path_logs>"; exit; }

SHA256_LIST_FILE=$1
DOWNLOAD_QUEUE=$2
EXTRACTION_QUEUE=$3
LOG_DIR=$4

SHA256_LIST_FILENAME=$(basename $SHA256_LIST_FILE)
DOWNLOADED_DIR=$DOWNLOAD_QUEUE/downloaded
# get the last line (sha256) of file
LAST_SHA256=$(tail -n 1 $SHA256_LIST_FILE)

# extrair APIKEY do arquivo txt do caminho X
APIKEY_ANDROZOO=$(cat "./inputs/androzoo/apikey_androzoo.txt")

while read SHA256 || [ -n "$SHA256" ]
do
	if [ -f $DOWNLOADED_DIR/$SHA256.apk ]
	then
		continue
	fi

	echo -n "Downloading APK $SHA256 ... "
	/usr/bin/time -f "$SHA256 Download Elapsed Time = %e seconds, CPU = %P, Memory = %M KiB" \
		-a -o $LOG_DIR/stats-"$SHA256_LIST_FILENAME".log curl -s -S -o $DOWNLOAD_QUEUE/$SHA256.apk \
		--remote-header-name -G -d apikey=$APIKEY_ANDROZOO \
		-d sha256=$SHA256 https://androzoo.uni.lu/api/download
	CURL_EXEC=$(echo $?)
	if [ -f $DOWNLOAD_QUEUE/$SHA256.apk ] && [ $CURL_EXEC -eq 0 ]
	then
		mv $DOWNLOAD_QUEUE/$SHA256.apk $DOWNLOADED_DIR/
	  touch $EXTRACTION_QUEUE/$SHA256.downloaded
	  echo "DONE"
	else
	  echo "ERROR"
	fi

	# check if the last APK of the file has already been downloaded
	if [ -f $DOWNLOADED_DIR/$LAST_SHA256.apk ]
	then
		mv $DOWNLOAD_QUEUE/$SHA256_LIST_FILENAME $DOWNLOAD_QUEUE/$SHA256_LIST_FILENAME.finished
	fi
done < $SHA256_LIST_FILE
