# 🧠 Ollama Gladiator — Benchmark de LLMs Multimodais Instalados via Ollama

Bem-vindo ao **Ollama Gladiator**, um projeto de **OCR baseado em LLMs Multimodais**, utilizando o **Ollama** como backend para execução local dos modelos multimodais instalados.

A proposta do projeto consiste na avaliação comparativa de diferentes LLMs multimodais “em uma arena”, com foco na extração de texto estruturado a partir de imagens.

---

## 🚀 Objetivo

O objetivo do projeto é **extrair texto de imagens utilizando modelos multimodais do Ollama**, forçando uma saída **padronizada e estruturada**.

Cada modelo processa a mesma imagem e gera:

- Arquivo `.txt` com as linhas OCR detectadas
- Arquivo `.json` estruturado a partir do OCR
- Resultados organizados por imagem **e por modelo**

Tudo isso de forma automatizada e totalmente local.

---

## 🧠 Tecnologias e Estrutura

- **Ollama**: Execução local dos modelos LLM (API REST na porta `11434`)
- **LLMs Multimodais Visuais** (podem ser modificados conforme os modelos instalados)
  - `llama3.2-vision`
  - `gemma3`
  - `ministral-3`
  - `qwen3-vl`
- **Prompt Engineering**: Controle rígido de formato de saída OCR
- **NDJSON Streaming**: Processamento contínuo da resposta dos modelos
- **Python**: Orquestração, parsing e persistência dos resultados

---

## 🛠️ Instalação

### 1️⃣ Pré-requisitos

- Python **3.10+**
- Ollama instalado e funcional (disponível em https://ollama.com/download)
- Modelos multimodais previamente baixados (disponível em https://ollama.com/search?c=vision) 
- Serviço do Ollama rodando em background

Exemplo de ativação do Ollama:
```bash
ollama serve
```

2️⃣ Dependências Python

Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```

🖼️ Como usar
1️⃣ Preparando as imagens

Você pode fornecer:

1 - Um arquivo de imagem individual
2 - Um diretório contendo várias imagens (recursivo)

Extensões suportadas:

.jpg .jpeg .png .bmp .tiff .webp

2️⃣ Execução

▶️ Processamento por arquivo
```bash
python3 ollama_extract.py imagem.jpg
```

▶️ Processamento por diretório
```bash
python3 ollama_extract.py pasta_de_imagens/
```

▶️ Múltiplas entradas
```bash
python3 ollama_extract.py imagem1.png imagem2.jpg pasta/
```

O script:

Expande automaticamente os caminhos

Processa cada imagem com todos os modelos configurados

Salva os resultados separadamente por modelo

⚙️ Funcionamento Interno

1 - A imagem é convertida para Base64 para suportar o uso da API na porta 11434
2 - O modelo recebe:
2.1 - Um prompt extremamente restritivo podendo ser personalizado
2.2 - A imagem embutida
2.3 - O retorno vem em NDJSON streaming

As respostas são concatenadas e separadas por linha. onde cada linha segue o formato:
```
OCR='texto', score=0.95, bbox=[x1,y1,x2,y2]
```
1 - O .txt é salvo

2 - O .txt é parseado em tokens

3 - Os tokens são convertidos em .json

📁 Estrutura dos Arquivos
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
