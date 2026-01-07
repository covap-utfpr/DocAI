import sys
import re
import json
import pandas as pd
from collections import Counter
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import matplotlib.pyplot as plt

# ---------------------------------------------
# Função para normalizar e quebrar texto em tokens
# Remove aspas, converte para maiúsculas, retira pontuação
# ---------------------------------------------
def normalizar_e_tokenizar(texto):
    texto = re.sub(r"[\'‘\"]", "", texto)   # Remove aspas            
    texto = texto.upper()                   # Converte para maiúsculas
    texto = re.sub(r"[^\w\s]", " ", texto)  # Remove pontuação
    tokens = texto.split()                  # Quebra em palavras
    return tokens

# ---------------------------------------------
# Função para extrair tokens de um arquivo JSON
# Retorna uma lista de tokens normalizados dos itens
# ---------------------------------------------
def extrair_json(path):
    tokens_totais = []
    try:
        with open(path, "r", encoding="utf-8") as arquivo:
            data = json.load(arquivo)

            # Processa a lista de itens
            if "itens" in data and isinstance(data["itens"], list):
                for item in data["itens"]:
                    # Extrai campos relevantes: código, descrição
                    if "codigo" in item and item["codigo"]:
                        tokens = normalizar_e_tokenizar(str(item["codigo"]))
                        tokens_totais.extend(tokens)                
                    if "descricao" in item and item["descricao"]:
                        tokens = normalizar_e_tokenizar(str(item["descricao"]))
                        tokens_totais.extend(tokens)
                    if "preco_total" in item and item["preco_total"]:
                        tokens = normalizar_e_tokenizar(str(item["preco_total"]))
                        tokens_totais.extend(tokens)
                    if "preco_unitario" in item and item["preco_unitario"]:
                        tokens = normalizar_e_tokenizar(str(item["preco_unitario"]))
                        tokens_totais.extend(tokens)    
                    if "quantidade" in item and item["quantidade"]:
                        tokens = normalizar_e_tokenizar(str(item["quantidade"]))
                        tokens_totais.extend(tokens)        
            if not tokens_totais:
                texto_completo = json.dumps(data, ensure_ascii=False)
                tokens_totais = normalizar_e_tokenizar(texto_completo)
    except Exception as e:
        print(f"Erro ao processar JSON em {path}: {e}")
    return tokens_totais

# ---------------------------------------------
# Função para extrair OCR='...' de um arquivo
# Retorna uma lista de tokens normalizados
# ---------------------------------------------
def extrair_ocr(path):                                      # Extrair o conteudo OCR do arquivo 
    padrao = re.compile(r"OCR='(.*?)'")                     # Extrair conteudo entre OCR=" "
    tokens_totais = []                                      # Lista de palavras extraidas 
    with open(path, "r", encoding="utf-8") as arquivo:      # abre o arquivo 
        for linha in arquivo:                               # para cada linha do arquivo
            conteudo = padrao.search(linha)                 # procure o padão (ocr)  
            if conteudo:                                    # se encontrou  
                texto = conteudo.group(1).strip()           # pegue o texto
                tokens = normalizar_e_tokenizar(texto)      # normalize e quebre em tokens
                tokens_totais.extend(tokens)                # adicione os tokens a lista total 
    return tokens_totais                                    # retorne a lista de tokens

# ---------------------------------------------
# Função universal para extrair tokens
# Detecta automaticamente se é TXT ou JSON
# ---------------------------------------------
def extrair_tokens(path):
    # Detecta o tipo de arquivo pela extensão
    if path.lower().endswith('.json'):
        return extrair_json(path)
    elif path.lower().endswith('.txt'):
        return extrair_ocr(path)
    else:
        # Tenta detectar pelo conteúdo
        try:
            with open(path, "r", encoding="utf-8") as f:
                primeira_linha = f.readline().strip()
                # Se começa com { ou [, provavelmente é JSON
                if primeira_linha.startswith('{') or primeira_linha.startswith('['):
                    return extrair_json(path)
                else:
                    return extrair_ocr(path)
        except:
            # Fallback para OCR
            return extrair_ocr(path)

# ---------------------------------------------
# Comparação entre base e cupom
# Leva em conta duplicados (cada item só pode ser "consumido" uma vez)
# ---------------------------------------------
def comparar_consumindo(base, cupom):                       # Comparação entre o cupom travado de referencia e os demais
    cupom_counter = Counter(cupom)                          # Contador de itens disponiveis no cupom
    cupom_pool = cupom.copy()                               # Para mostrar visualmente o conteúdo consumido
    contem = []                                             # Lista booleana: True se item encontrado
    con_encontrado = []                                     # Lista do item encontrado (para visualização)
    for item in base:                                       # Para cada item no cupom de referencia 
        if cupom_counter[item] > 0:                         # Se o item é encontrado no cupom             
            contem.append(True)                             # Item presente → OK
            con_encontrado.append(item)                     # Adiciona o item a con_encontrado
            cupom_counter[item] -= 1                        # consome uma linha do contador 
            if item in cupom_pool:                          # Se o item ainda está no pool
                cupom_pool.remove(item)                     # Remove do pool visual
        else:                                               # Se o item não é encontrado no cupom             
            contem.append(False)                            # Item ausente → ERR            
            if cupom_pool:                                  # Se ainda há itens no pool
                con_encontrado.append(cupom_pool.pop(0))    # Adiciona o próximo item do pool
            else:                                           # Se o pool está vazio
                con_encontrado.append("")                   # Adiciona a string vazia
    return contem, con_encontrado                           # retorna lista de booleanos e conteudo encontrado

# ---------------------------------------------
# Calcula métricas básicas de classificação
# ---------------------------------------------
def calcular_metricas(base, cupom, contem):                 # Métricas de classificação 
    base_counter = Counter(base)                            # Contador de itens no cupom base        
    cup_counter = Counter(cupom)                            # Contador de itens no cupom a ser comparado 
    TP = sum(contem)                                        # Verdadeiros positivos
    FN = len(base) - TP                                     # Falsos negativos
    FP = 0                                                  # Falsos positivos
    for item, qtd in cup_counter.items():                   # Para cada item no cupom comapado
        excesso = qtd - base_counter.get(item, 0)           # Verifique se há excesso em relaçaõ ao contador da base
        if excesso > 0:                                     # Se houver
            FP += excesso                                   # Adicione ao total de falsos positivos
    TN = 0                                                  # Não utilizado no momento

    # Métricas clássicas
    acuracia = TP / len(base) if len(base) else 0           # Acurácia = Verdadeiros positivos / Total de itens na base
    precisao = TP / (TP + FP) if (TP + FP) else 0           # Precisão = Verdadeiros positivos / (Verdadeiros positivos + Falsos positivos) 
    recall = TP / (TP + FN) if (TP + FN) else 0             # Recall = Verdadeiros positivos / (Verdadeiros positivos + Falsos negativos) 
    f1 = 2 * precisao * recall / (precisao + recall) if (precisao + recall) else 0 # F1 Score = 2 * (Precisão * Recall) / (Precisão + Recall)

    return {                    # Retorne
        "TP": TP,               # Verdadeiros positivos
        "FP": FP,               # Falsos positivos
        "FN": FN,               # Falsos negativos
        "TN": TN,               # Verdadeiros negativos
        "Acuracia": acuracia,   # Acurácia 
        "Precisao": precisao,   # Precisão 
        "Recall": recall,       # Recall
        "F1": f1                # F1 Score
    }

# ---------------------------------------------
# MAIN
# ---------------------------------------------
def main():                                                                         # Função principal
    if len(sys.argv) < 3:                                                           # Verifica se possui pelo menos 2 argumentos (base + 1 cupom)
        print("Uso: python3 compare.py base.txt cupom1.txt cupom2.txt ...")         # Instruções de uso
        print("Aceita arquivos .txt (OCR) e .json")                                 # Instruções de uso
        return                                                                      # Encerra a função 

    base_path = sys.argv[1]                                                         # Caminho do arquivo base
    base_nome = base_path.replace(".txt", "").replace(".json", "").split("/")[-1]   # Nome da base sem extensão e caminho
    base = extrair_tokens(base_path)                                                # Extrai tokens da base (função)
    print(f"Base '{base_nome}' carregada: {len(base)} tokens")                      # Mensagem de status
    cupons_paths = sys.argv[2:]                                                     # Caminhos dos arquivos de cupons a serem comparados  
    nomes_cupons = [p.replace(".txt", "").split("/")[-1] for p in cupons_paths]     # Nomes dos cupons sem extensão e caminho
    df_resultado = pd.DataFrame({"ITEM_BASE": base})                                # DataFrame para resultados (booleanos) 
    df_conteudo = pd.DataFrame({"ITEM_BASE": base})                                 # DataFrame para conteúdos encontrados 
    metricas_total = {}                                                             # Dicionário para armazenar métricas totais por cupom

    # ---------------------------------------------
    # Loop pelos cupons
    # ---------------------------------------------
    for path, nome in zip(cupons_paths, nomes_cupons):                  # Para cada caminho e nome de cupom em zip (lista paralela)
        cupom = extrair_tokens(path)                                    # Extrai tokens do cupom (função)
        print(f"Cupom '{nome}' carregado: {len(cupom)} tokens")         # Mensagem de status 
        contem, conteudo = comparar_consumindo(base, cupom)             # Compara base e cupom (função)
        df_resultado[nome] = contem                                     # DataFrame de resultados (booleanos)
        df_conteudo[nome] = conteudo                                    # DataFrame de conteúdos encontrados
        metricas_total[nome] = calcular_metricas(base, cupom, contem)   # Métricas do cupom (funçaõ)

    # ---------------------------------------------
    # Criar XLSX
    # ---------------------------------------------
    wb = Workbook()                                                                         # Cria novo workbook do Excel (xlsx) 
    fill_ok = PatternFill(start_color="CCFFCC", end_color="CCFFCC", fill_type="solid")      # Se o conteúdo foi encontrado pinte de verde
    fill_err = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")     # Se o conteúdo não foi encontrado pinte de vermelho
    fill_empate = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")  # Se houve empate pinte de amarelo

    # ABA 1 — RESULTADO
    ws1 = wb.active                                                                 # Primeira aba  
    ws1.title = "Resultado"                                                         # Nomeada de Resultado
    ws1.append([f"BASE: {base_nome}"] + [f"COMP: {n}" for n in nomes_cupons])       # Cabeçalho com nomes
    ws1.append(list(df_resultado.columns))                                          # Cabeçalho com colunas

    for i in range(len(df_resultado)):                                              # Para cada linha do DataFrame de resultados
        for j, col in enumerate(df_resultado.columns, start=1):                     # Para cada coluna 
            cell = ws1.cell(row=i + 3, column=j)                                    # Célula recebe valor de linha e coluna  
            if col == "ITEM_BASE":                                                  # Se a coluna for ITEM_BASE 
                cell.value = df_resultado.iloc[i, 0]                                # Apenas copie o valor 
                continue                                                            # Vá para a próxima iteração 
            status = df_resultado.iloc[i, j-1]                                      # Obtenha o valor booleano  
            cell.value = "CONTÉM" if status else "NÃO CONTÉM"                       # Defina o valor da célula como CONTÉM ou NÃO CONTÉM
            cell.fill = fill_ok if status else fill_err                             # Pinte a célula de acordo com o status 

    # ABA 2 — CONTEÚDO  
    ws2 = wb.create_sheet("Conteudo")                                               # Segunda aba 

    ws2.append([f"BASE: {base_nome}"] + [f"COMP: {n}" for n in nomes_cupons])       # Cabeçalho com nomes
    ws2.append(list(df_conteudo.columns))                                           # Cabeçalho com colunas
    for i in range(len(df_conteudo)):                                               # Para cada linha do DataFrame de conteúdos
        for j, col in enumerate(df_conteudo.columns, start=1):                      # Para cada coluna
            cell = ws2.cell(row=i + 3, column=j)                                    # Célula recebe valor de linha e coluna  
            value = df_conteudo.iloc[i, j-1]                                        # Valor daa célula
            cell.value = value                                                      # Defina o valor da célulaa
            if col == "ITEM_BASE":                                                  # Se a coluna for ITEM_BASE
                continue                                                            # Vá para a próxima iteração
            status = df_resultado.iloc[i, j-1]                                      # Obtenha o valor booleano correspondente
            cell.fill = fill_ok if status else fill_err                             # Pinte a célula de acordo com o status

    # ABA 3 — MÉTRICAS
    ws3 = wb.create_sheet("Metricas")                                               # Terceira aba
    cab = ["CUPOM", "TP", "FP", "FN", "TN", "Acuracia", "Precisao", "Recall", "F1"] # Cabeçalho das métricas
    ws3.append(cab)                                                                 # Adiciona o cabeçalho
    for nome, m in metricas_total.items():                                          # Para cada cupom e suas métricas
        ws3.append([                                                                # Adiciona uma linha com as métricas
            nome, m["TP"], m["FP"], m["FN"], m["TN"],
            m["Acuracia"], m["Precisao"], m["Recall"], m["F1"]
        ])

    # ABA 4 — CONSENSUS
    ws4 = wb.create_sheet("Consensus")                                  # Quarta Aba 
    ws4.append(["ITEM_BASE", "ACERTOS", "ERROS", "CONSENSUS"])          # Cabeçalho da aba
    for i, item in enumerate(df_resultado["ITEM_BASE"]):                # Para cada item na coluna ITEM_BASE
        resultados = df_resultado.iloc[i, 1:].tolist()                  # Resultados dos cupons (exclui ITEM_BASE) 
        acertos = sum(resultados)                                       # Conta acertos (True = 1)
        erros = len(resultados) - acertos                               # Conta erros (False = 0) 
        if acertos > erros:                                             # Se acertos são maioria 
            consenso = "OK"                                             # Define consenso como OK  
            fill = fill_ok                                              # Pinta de verde
        elif erros > acertos:                                           # Se erros são maioria 
            consenso = "ERR"                                            # Define consenso como ERR 
            fill = fill_err                                             # Pinta de vermelho
        else:                                                           # Se empate
            consenso = "EMPATE"                                         # Define consenso como EMPATE
            fill = fill_empate                                          # Pinta de amarelo
        ws4.append([item, acertos, erros, consenso])                    # Adiciona a linha na planilhaa
        ws4.cell(row=ws4.max_row, column=4).fill = fill                 # Pinta a célula de consenso
    
    # ABA 5 — GRÁFICO LONGO DE ACERTOS/ERROS    
    if len(base) > 0 and len(nomes_cupons) > 0:                         # Verificação antes de gerar o gráfico
        ws5 = wb.create_sheet("Grafico")                                # Quinta aba para gráfico        
        for i, nome in enumerate(nomes_cupons):                         # Para cada cupom analisado
            ws5.append([nome] + df_resultado[nome].astype(int).tolist())# Adiciona os dados do cupom (1 para True, 0 para false)
        itens_base = df_resultado["ITEM_BASE"].tolist()                 # Para o eixo X do gráfico
        x = range(len(itens_base))                                      # Eixo X numérico com base no número de itens
        plt.figure(figsize=(max(len(itens_base)*0.4, 8), 6))            # Figura maior para muitos itens, ajustando largura baseado em número de itens, altura fixa 
        offset = 0.03                                                   # distância entre linhas
        for i, nome in enumerate(nomes_cupons):                         # Para cada cupom analisado
            y = df_resultado[nome].astype(int) + i*offset               # Eixo Y com offset para visualização
            plt.plot(x, y, marker='o', label=nome)                      # Plota a linha com marcadores
        save_name = (f"grafico_comparacao_{base_nome}_" + ".png")       # Nome do arquivo de saída a ser salvo

        plt.xticks(x, itens_base, rotation=90)                          # Mostra os nomes dos itens na horizontal
        plt.xlabel("Item Base")                                         # Rótulo do eixo X
        plt.ylabel("Acerto (1) / Erro (0)")                             # Rótulo do eixo Y
        plt.title("Acertos e Erros por Cupom")                          # Título do gráfico
        plt.legend(loc='lower left')                                    # Legenda no canto inferior esquerdo
        plt.tight_layout()                                              # Ajuste automático do layoult
        plt.grid(True, linestyle='--', alpha=0.5)                       # Adiciona grade ao gráfico
        plt.yticks([0, 1], ["Erro (0)", "Acerto (1)"])                  # Rótulos do eixo Y
        plt.ylim(-0.1, 1 + len(nomes_cupons)*offset + 0.1)              # Limites do eixo Y    
        plt.savefig(save_name)                                          # Salva o gráfico como imagm        
        plt.close()                                                     # Fecha a figura para liberar memória
        print("Gráfico salvo: grafico_acertos_erros_longo.png")         # Mensagem de status
    else:                                                               # Se não há dados avisa
        print("AVISO: Não há dados suficientes para gerar o gráfico")   # Mensagem de aviso
    output_file = f"comparacao_{base_nome}.xlsx"                        # Salvar arquivo XLSX
    wb.save(output_file)                                                # Salva o arquivo XLSX
    print(f"\nArquivo gerado: {output_file}")                           # Mensagem de status
    
    if len(base) == 0:                                                                                                  # Verifica se a base está vazia
        print("\nAVISO: A base não contém tokens! Verifique o formato do arquivo.")                                     # Se estiver, avisa o usuário
        print("Para JSON, certifique-se que possui a estrutura: {\"itens\": [{\"codigo\": ..., \"descricao\": ...}]}")  # Se estiver, avisa o usuário#
        print("Para TXT, certifique-se que possui linhas no formato: OCR='...'")                                        # Se estiver, avisa o usuário

if __name__ == "__main__":  # Execução do main
    main()                  # Chama a função principal