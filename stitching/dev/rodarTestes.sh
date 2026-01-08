N=3 #Numero de vezes a testar

for i in $(seq 0 $N)
do
   echo "===================================Execução número: $i================================================"

   	#Ajuste a pasta do data base
	sed -i "s|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/$((i-1))|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/$i|g" mosaico_01.py  	
	#execute o algoritimo
  	python3.9 mosaico_01.py
done

#Restaure o arquivo como estava inicialmente
sed -i "s|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/$i|/home/atosarruda/Documentos/IC - Erikson/DocAI/stitching/db/0|g" mosaico_01.py 