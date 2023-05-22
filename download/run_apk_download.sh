[ $1 ] && [ -f $1 ] && [ $2 ] && [ -d $2 ] && [ $3 ] && [ -d $3 ] && [ $4 ] && [ -d $4 ] || { echo "Usage: $0 <APK_SHA256_list.txt> <path_download_queue> <path_extraction_queue> <path_logs>"; exit; }

SHA256_LIST_FILE=$1
DOWNLOAD_QUEUE=$2
EXTRACTION_QUEUE=$3
LOG_DIR=$4

SHA256_LIST_FILENAME=$(basename $SHA256_LIST_FILE)
DOWNLOADED_DIR=$DOWNLOAD_QUEUE/downloaded
# pegar última linha (sha256) do arquivo
LAST_SHA256=$(tail -n 1 $SHA256_LIST_FILE)

while read SHA256 || [ -n "$SHA256" ]
do
	if [ -f $DOWNLOADED_DIR/$SHA256.apk ]
	then
		continue
	fi

	#AndroZoo Another API Key: 44e1937815802c68ee461e4f186f388107ad2ac5f10d0a38f93de5d56a7420ec
	echo -n "Downloading APK $SHA256 ... "
	/usr/bin/time -f "$SHA256 Download Elapsed Time = %e seconds, CPU = %P, Memory = %M KiB" \
		-a -o $LOG_DIR/stats-"$SHA256_LIST_FILENAME".log curl -s -S -o $DOWNLOAD_QUEUE/$SHA256.apk \
		--remote-header-name -G -d apikey=fa08a4ad8d8c9d3c56236d27bd9b99bb83c66c3fd65642d496ea2cbd13d4e8a4 \
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

	# verificar se o último APK do arquivo já foi baixado
	if [ -f $DOWNLOADED_DIR/$LAST_SHA256.apk ]
	then
		mv $DOWNLOAD_QUEUE/$SHA256_LIST_FILENAME $DOWNLOAD_QUEUE/$SHA256_LIST_FILENAME.finished
	fi
done < $SHA256_LIST_FILE
