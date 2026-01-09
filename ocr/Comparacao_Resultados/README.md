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
- Suportar automaticamente arquivos **TXT (OCR)** e **JSON estruturado**
- Organizar todos os resultados em pastas por base dentro da pasta `results`
---

## 🧠 Tecnologias Utilizadas

- **Python 3**
- **Pandas** — Estruturação dos dados
- **OpenPyXL** — Criação e formatação de planilhas Excel
- **Matplotlib / Seaborn** — Visualização gráfica (acertos/erros e granularidade)
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

O tipo de arquivo é detectado automaticamente com base na extensão ou conteúdo.

📄 TXT (OCR)
Os arquivos .txt devem conter linhas no padrão:
```bash
OCR='Texto reconhecido pelo OCR'
```
O script extrai automaticamente o conteúdo entre OCR='...'.

🗂️ JSON (Estruturado)
Estrutura esperada (preferencial):
```
{
  "itens": [
    {
      "codigo": "123",
      "descricao": "PRODUTO X",
      "quantidade": 2,
      "preco_unitario": 10.00,
      "preco_total": 20.00
    }
  ]
}
```
Campos relevantes são automaticamente tokenizados.
Caso a estrutura não seja detectada, o sistema realiza fallback, tokenizando todo o conteúdo JSON.


▶️ Como Usar
Execução via terminal
```bash
python3 compare.py base.json cupom1.txt cupom2.json cupom3.txt
```
O primeiro arquivo é sempre tratado como base de referência
Os demais são cupons comparativos
Arquivos .txt e .json podem ser combinados livremente

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

Todos os arquivos são salvos na pasta:
```
results/<nome_base>_results/
```
Exemplo: ```results/minha_base_results/```

O arquivo ```.xlsx``` possui as seguintes abas:

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

📉 Gráficos
1 - Acertos e Erros por cupom
- Salvo como:
```
results/<base>_results/grafico_comparacao_<base>.png
```

2 - Matriz de Granularidade Simétrica (visualização)
- Heatmap baseado na média de cobertura mútua entre cupons
- Salvo como:
```
results/<base>_results/granularidade_<base>.png
```
Observação: A matriz real de granularidade (linha A em relação à coluna B) está disponível no Excel.

##  📌 Observações finais
    O projeto ainda está em desenvolvimento — fique à vontade para sugerir melhorias!
