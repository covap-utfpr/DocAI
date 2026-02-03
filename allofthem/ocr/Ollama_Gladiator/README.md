# 🧠 Ollama Gladiator — Benchmark de OCR com LLMs Multimodais via Ollama

O **Ollama Gladiator** é um projeto de **OCR baseado em LLMs multimodais**, executados localmente via **Ollama**, com foco em **benchmark comparativo e análise direta** entre modelos visuais.

A proposta é colocar diferentes LLMs multimodais em uma “arena”, processando a **mesma imagem** para avaliar **qualidade, consistência e estrutura do OCR** gerado, com saída padronizada.

Os modelos atualmente configurados para execução no script `ollama_extract.py` são:

```python
MODELOS_INSTALADOS = [
  "llama3.2-vision:11b",
  "gemma3:4b",
  "gemma3:12b",
  "ministral-3:3b",
  "ministral-3:8b",
  "ministral-3:14b",
  "qwen3-vl:2b",
  "qwen3-vl:4b",
  "qwen3-vl:8b",
]
```
Outros modelos multimodais podem ser adicionados ou removidos facilmente conforme desejado.

Os modelos disponíveis podem ser consultados em: https://ollama.com/search?c=vision

Basta modificar a lista `MODELOS_INSTALADOS`.

## 🚀 Objetivo

O objetivo do projeto é **extrair texto de imagens utilizando modelos multimodais do Ollama**, forçando uma saída **padronizada e estruturada**.

Cada modelo processa a mesma entrada, permitindo avaliação comparativa e gerando:

- Arquivo `.txt` com as linhas OCR detectadas
- Arquivo `.json` estruturado a partir do OCR
- Resultados organizados por imagem **e por modelo**

Tudo isso de forma automatizada e totalmente local.

## 🧠 Tecnologias e Estrutura

- **Ollama**: Execução local dos modelos LLM (API REST na porta `11434`)
- **LLMs Multimodais Visuais** (podem ser modificados conforme os modelos instalados localmente)
  - `gemma3 (4b e 12b)`
  - `llama3.2-vision (11b)`
  - `ministral-3 (3b, 8b e 14b)`
  - `qwen3-vl (2b, 4b e 8b)`
- **Prompt Engineering**: Controle rígido de formato de saída OCR
- **NDJSON Streaming**: Processamento contínuo da resposta dos modelos
- **Python**: Orquestração, parsing e persistência dos resultados

## 🛠️ Instalação

### 1️⃣ Pré-requisitos

- Python **3.10+**
- Ollama instalado e funcional (disponível em https://ollama.com/download)
- Modelos multimodais previamente baixados
- Serviço do Ollama rodando em background

Exemplo de ativação do Ollama:
```bash
ollama serve
```

### 2️⃣ Dependências Python

Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```

## 🖼️ Como usar

### 1️⃣ Preparando as imagens

Você pode fornecer:

- Um arquivo de imagem individual
- Um diretório contendo várias imagens (recursivo)

Extensões suportadas:
```
.jpg .jpeg .png .bmp .tiff .webp
```

### 2️⃣ Execução

- ▶️ Processamento por arquivo
```bash
python3 ollama_extract.py imagem.jpg
```

- ▶️ Processamento por diretório
```bash
python3 ollama_extract.py pasta_de_imagens/
```

- ▶️ Múltiplas entradas
```bash
python3 ollama_extract.py imagem1.png imagem2.jpg pasta/
```

O script:

- Expande automaticamente os caminhos
- Processa cada imagem com todos os modelos configurados
- Salva os resultados separadamente por modelo

## ⚙️ Funcionamento Interno

- A imagem é convertida para Base64 para suportar o uso da API na porta 11434
- O modelo recebe:
  - Um prompt extremamente restritivo podendo ser personalizado (função `extract_text_from_image`)
  - A imagem embutida
  - O retorno vem em NDJSON streaming

As respostas são concatenadas e separadas por linha onde cada linha segue o formato:
```
OCR='texto', score=0.95, bbox=[x1,y1,x2,y2]
```
- O .txt é salvo
- O .txt é parseado em tokens
- Os tokens são convertidos em .json

## 📁 Estrutura dos Arquivos
```
ollama_extract.py          # Script principal (OCR multimodelo)
Modules/
├── config.py              # Parse dos arquivos OCR (.txt)
├── json_processing.py     # Limpeza, conversão e salvamento em JSON
├── path.py                # Gerenciamento de diretórios
images/                    # (Opcional) Pasta de imagens para ser carregado
results/                   # Resultados gerados por imagem e modelo
```

Exemplo de saída:
```
results/
├── nota_fiscal_llama3.2-vision_ocr.txt
├── nota_fiscal_llama3.2-vision.json
├── nota_fiscal_gemma3_ocr.txt
├── nota_fiscal_gemma3.json
```

##  📌 Observações finais
    O projeto ainda está em desenvolvimento — fique à vontade para sugerir melhorias!
