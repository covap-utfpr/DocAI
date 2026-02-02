cd ERCSF_1
sed -i "s|op = 1|op = 3|g" mosaico_cs.py
sed -i "s|saltoFixo = 1|saltoFixo = 1|g" mosaico_cs.py
./rodarTestes.sh
cd ..

cd ERCSF_2
sed -i "s|op = 1|op = 3|g" mosaico_cs.py
sed -i "s|saltoFixo = 1|saltoFixo = 2|g" mosaico_cs.py
./rodarTestes.sh
cd ..

cd ERCSF_3
sed -i "s|op = 1|op = 3|g" mosaico_cs.py
sed -i "s|saltoFixo = 1|saltoFixo = 3|g" mosaico_cs.py
./rodarTestes.sh
cd ..


cd SCS_1
sed -i "s|op = 1|op = 4|g" mosaico_cs.py
sed -i "s|saltoFixo = 1|saltoFixo = 1|g" mosaico_cs.py
./rodarTestes.sh
cd ..

cd SCS_2
sed -i "s|op = 1|op = 4|g" mosaico_cs.py
sed -i "s|saltoFixo = 1|saltoFixo = 2|g" mosaico_cs.py
./rodarTestes.sh
cd ..

cd SCS_3
sed -i "s|op = 1|op = 4|g" mosaico_cs.py
sed -i "s|saltoFixo = 1|saltoFixo = 3|g" mosaico_cs.py
./rodarTestes.sh
cd ..