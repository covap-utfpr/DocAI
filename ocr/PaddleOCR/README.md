# 📄 Projeto OCR com PaddleOCR + Matplotlib + Spellchecker

Bem-vindo ao projeto de **Reconhecimento Óptico de Caracteres (OCR)** utilizando **PaddleOCR** integrado ao **Matplotlib** para visualização dos resultados. 

Projetado para ser simples de usar e com suporte a uma interface gráfica para testes manuais.

---

## 🚀 Objetivo

O projeto tem como foco identificar e extrair texto de imagens, utilizando PaddleOCR. 

Além disso, apresenta visualizações dos resultados com Matplotlib, salvando tanto as imagens plotadas quanto os dados em arquivos `.txt` e `.json`.

Possui alguns corretores ortográficos (`pyspellchecker, autocorrect`) para validar o conteúdo extraido (ainda em ajustes).

---
## 🧠 Tecnologias e Estrutura

- **PaddleOCR**: Motor OCR para identificação dos textos nas imagens.
- **Matplotlib**: Para exibir visualmente os resultados com bounding boxes.
- **Corretores**: Usados para validar e corrigir o conteúdo identificado.
- **EasyGUI**: Interface gráfica simples para uso manual.
---

## 🛠️ Instalação

Clone o repositório e instale as dependencias do requirements.txt lembrando que as dependencias foram construidas para utilizar **CUDA Version: 12.2** 

## 🖼️ Como usar
## 1. Preparando as imagens

Coloque as imagens que deseja processar na pasta (não é obrigatório ser esse diretório podendo ser passado por parametro ou selecionado por interface grafica):

images/

## 2. Execução
   
⚠️ Atenção! Verifique se você está dentro do venv ```PaddleOCR```, se não estiver ative via ```source bin/activate```

A execução do PaddleGUI é simples e gira em torno da escolha das imagens e da ativação (ou não) dos módulos auxiliares. O script aceita tanto uso direto via terminal quanto seleção gráfica de arquivos pelo EasyGUI.

▶️ Modo padrão (EasyGUI)

Se você rodar o script sem argumentos, o sistema abre uma janela para selecionar uma ou várias imagens (segure a tecla shift para selecionar as imagens desejadas):
```
python3.12 PaddleGUI.py
```
Basta escolher os arquivos e confirmar. O OCR será executado, a imagem será plotada com as marcações e os resultados serão salvos em Results_OCR.

▶️ Processamento direto por argumento

Você também pode indicar uma imagem ou um diretório:
```
python3.12 PaddleGUI.py imagem.jpg
python3.12 PaddleGUI.py pasta_de_imagens/
```
O script identifica automaticamente cada arquivo válido e processa tudo em sequência (nesse modo de terminal ele não exibe em tela a plotagem, mas salva em Results_OCR).

⚙️ Opções adicionais

Use os argumentos opcionais para controlar módulos internos:

Flag	Função
```
--nospell	Desativa o corretor ortográfico
--nojson	Desativa a saída JSON
--disable-all	Desativa corretor + JSON (tem prioridade total)
```
exemplos:
```
python3.12 PaddleGUI.py imagem.jpg --nospell
python3.12 PaddleGUI.py imagem.jpg --nojson
python3.12 PaddleGUI.py pasta/ --disable-all

```
🆘 Ajuda integrada   
Para visualizar o menu de ajuda:
```
python3.12 PaddleGUI.py --help
```

📁 Estrutura dos arquivos

```
PaddleGUI.py              # Script principal do OCR + visualização
Modules/
├── config.py             # Configurações gerais (OCR, fonte, validações)
├── image_processing.py   # Lógica de plotagem com Matplotlib
├── json_sprocessing.py   # Gera JSON estruturado a partir dos resultados
├── path.py               # Manipulação de diretórios e caminhos
└── spellchecker.py       # Arquivo onde está a lógica dos corretores ortográficos
images/                   # Pasta onde você coloca suas imagens
results_OCR/              # Todos os Resultados processados [imagem com plotagem, txt de saida e .json]
```
##  📌 Observações finais

    O projeto ainda está em desenvolvimento — fique à vontade para sugerir melhorias!