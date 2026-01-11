N=30 #Numero de vezes a testar

ARQUIVO_LOG="resultados_mosaico.csv"

# Cria o cabeçalho da tabela (se o arquivo não existir)
if [ ! -f $ARQUIVO_LOG ]; then
    echo "Execucao,Tempo_Segundos,Numero_Imagens,Numero_Imaagens_Coladas,Numero_Find_matching,Numero_Sift" > $ARQUIVO_LOG	
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
  	saida_python=$(python3.9 mosaico_01.py)


  	fim_item=$(date +%s)
  	tempo_item=$((fim_item - inicio_item))

	numero_imagens=$(echo "$saida_python" | grep "nIMAGENS:" | cut -d':' -f2)
	numero_find_matching_sift=$(echo "$saida_python" | grep "FINDMATCHINGSIFT:" | cut -d':' -f2)
	numero_imagens_coladas=$(echo "$saida_python" | grep "IMAGENSCOLADAS:" | cut -d':' -f2)

	echo "$i,$tempo_item,$numero_imagens,$numero_imagens_coladas,$numero_find_matching_sift,$((2 * numero_find_matching_sift))" >> $ARQUIVO_LOG
done


fim_total=$(date +%s)



echo "TEMPO FINAL, $((fim_total-inicio_total))" >> $ARQUIVO_LOG


#Restaure o arquivo como estava inicialmente
sed -i "s|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/$i|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/0|g" mosaico_01.py 