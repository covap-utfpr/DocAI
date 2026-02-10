#------------------------------------------------
#CONFIGURAÇÃO
#------------------------------------------------

#CONFIGURAÇÕES BÁSICAS
EXEC=python3.13

#Dir/exec
PERSPECTIVA=scan/perspectiva.py 
TRATA=scan/trata.py 
MOSAICO =stitching/mosaico_cs.py
INPUT?=input
DEBUG=False # True or False


#CONFUGARAÇÕES PERSPECTIVA.PY
export PASTA_ENTRADA_PERSPECTIVA=$(INPUT)
export PASTA_SAIDA_PERSPECTIVA=/home/atosarruda/Documentos/IC - Erikson/DocAI/allofthem/output/perspectiva_output

#CONFIGURAÇÕES MOSAICO_CS.PY
export CAMINHO_NOTINHA = $(PASTA_SAIDA_PERSPECTIVA)
export DEBUG_MOSAICO = $(DEBUG)
export SELECAO = 4 # 1 - ERCS ; 2 - SCS ; 3 - ERCSF ; 4 SCSF
export TAMANHO_DO_SALTO = 2
export PASTA_SAIDA_MOSAICO=output/mosaico_output

#CONFUGARAÇÕES TRATA.PY
export PASTA_ENTRADA_TRATA=$(PASTA_SAIDA_MOSAICO)
export PASTA_SAIDA_TRATA=output/trata_output



all: 

	make run_perspectiva
	make run_mosaico_cs
	make run_trata
	make run_ocr

run_perspectiva:

	$(EXEC) $(PERSPECTIVA) 

run_mosaico_cs:

	$(EXEC) $(MOSAICO)

run_trata: 

	$(EXEC) $(TRATA)

run_ocr:

	bash ocr/Run_OCR.sh $(PASTA_SAIDA_TRATA)