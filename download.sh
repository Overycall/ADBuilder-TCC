[ "$1" ] &&  [ -f "$1" ] || { echo "Uso: $0 <sha256.txt>"; exit;}
while read SHA256

do  
  start=$(date +%s)
	# criar pastas CSVs e API_Calls_Zip, se não existir
	[ -d CSVs ] || mkdir CSVs
	[ -d API_Calls_Zip ] || mkdir API_Calls_Zip
	echo -n "Realizando o download do APK $SHA256 ... "
	curl -s -S -O --remote-header-name -G -d apikey=44e1937815802c68ee461e4f186f388107ad2ac5f10d0a38f93de5d56a7420ec -d sha256=$SHA256 https://androzoo.uni.lu/api/download
	echo "Download finalizado!!!"
	echo "Começando a extração de características..."
	python3 get_caracteristicas.py -a $SHA256".apk"
	echo "Gerado o CSV do APK!!!"
	end=$(date +%s)
	gzip -f $SHA256".csv"
	SHA256_UPPER=$(echo $SHA256 | tr '[:lower:]' '[:upper:]')
	mv $SHA256_UPPER".csv.gz" "CSVs/"
	mv $SHA256_UPPER"_API_Calls_original.zip" "API_Calls_Zip/"
  echo $SHA256_UPPER "Levou: $(($end-$start)) segundos" >> log_"$1".txt 
done < "$1"