N=3 #Numero de vezes a testar

ARQUIVO_LOG="resultados_mosaico.csv"

# Cria o cabeçalho da tabela (se o arquivo não existir)
if [ ! -f $ARQUIVO_LOG ]; then
    echo "Execucao,Tempo_Segundos" > $ARQUIVO_LOG	
fi

# Captura o tempo de início total
inicio_total=$(date +%s)

for i in $(seq 0 $N)
do


   echo "===================================Execução número: $i================================================"

   	#Ajuste a pasta do data base
	sed -i "s|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/$((i-1))|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/$i|g" mosaico_01.py  	
	sed -i "s|result_file_name = \"mosaico_.*\.jpg\"|result_file_name = \"mosaico_$i.jpg\"|g" mosaico_01.py

	# Captura o tempo de início de cada execução
	inicio_item=$(date +%s)

	#execute o algoritimo
  	python3.9 mosaico_01.py

  	fim_item=$(date +%s)
  	tempo_item=$((fim_item - inicio_item))

  	echo "$i,$tempo_item" >> $ARQUIVO_LOG
done


fim_total=$(date +%s)
#Restaure o arquivo como estava inicialmente
sed -i "s|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/$i|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/0|g" mosaico_01.py 