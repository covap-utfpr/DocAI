# 📊 Comparação e Avaliação de Resultados OCR

Projeto desenvolvido para **comparar, validar e avaliar resultados de OCR**, utilizando uma base de referência e múltiplos cupons comparativos.

O sistema gera relatórios completos em **Excel**, métricas clássicas de classificação e um **gráfico visual de acertos e erros**, facilitando análises quantitativas e qualitativas.

---

## 🎯 Objetivo

- Comparar textos extraídos por OCR de forma justa e controlada
- Considerar **duplicidades reais** de tokens
- Calcular métricas de desempenho (TP, FP, FN, etc.)
- Gerar relatórios profissionais em `.xlsx`
- Visualizar padrões de erro e acerto entre diferentes OCRs

---

## 🧠 Tecnologias Utilizadas

- **Python 3**
- **Pandas** — Estruturação dos dados
- **OpenPyXL** — Criação e formatação de planilhas Excel
- **Matplotlib** — Visualização gráfica
- **Regex (re)** — Extração e limpeza dos textos OCR
- **Counter (collections)** — Controle de consumo de tokens

---

## 🛠️ Instalação

Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```
Recomenda-se o uso de ambiente virtual (venv).

🧾 Formato dos Arquivos de Entrada

Os arquivos .txt devem conter linhas no padrão:
```bash
OCR='Texto reconhecido pelo OCR'
```
O script extrai automaticamente o conteúdo entre OCR='...'.

▶️ Como Usar
Execução via terminal
```bash
python3 compare.py base.txt cupom1.txt cupom2.txt cupom3.txt
```
O primeiro arquivo é sempre tratado como base de referência
Os demais são cupons comparativos

🔍 Funcionamento Interno

1️⃣ Normalização do Texto
- Remoção de aspas
- Conversão para maiúsculas
- Remoção de pontuação
- Tokenização por palavra

2️⃣ Comparação com Consumo Controlado
- Cada token da base só pode ser usado uma vez
- Evita falsos positivos por repetição
- Simula validação realista de OCR

3️⃣ Métricas Calculadas
- Verdadeiros Positivos (TP)
- Falsos Positivos (FP)
- Falsos Negativos (FN)
- Acurácia
- Precisão
- Recall
- F1-Score

📁 Estrutura do Relatório Excel

O script gera um arquivo .xlsx com as seguintes abas:

🟢 Resultado
- Indica se cada item da base foi encontrado
- Verde → CONTÉM
- Vermelho → NÃO CONTÉM

📦 Conteudo
- Mostra o conteúdo encontrado em cada comparação
- Facilita auditoria manual

📈 Metricas
- Tabela consolidada de métricas por cupom

🤝 Consensus
- Avaliação global entre todos os cupons
- Resultados:
- OK (maioria acerta)
- ERR (maioria erra)
- EMPATE

📉 Grafico
- Base para visualização longitudinal
- Gráfico salvo como:
```
grafico_acertos_erros_longo.png
```

##  📌 Observações finais
    O projeto ainda está em desenvolvimento — fique à vontade para sugerir melhorias!
