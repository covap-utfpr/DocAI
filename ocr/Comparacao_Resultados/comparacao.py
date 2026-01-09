import os
import sys
import re
import json
import pandas as pd
from collections import Counter
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import matplotlib.pyplot as plt
import seaborn as sns

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

            # Processa campos de cabeçalho
            campos_cabecalho = ["chave_de_acesso", "cnpj_estabelecimento", "cpf", "data_emissao", "nome_estabelecimento", "total_itens", "valor_total", "valor_total_pago"]
            for campo in campos_cabecalho:
                if campo in data and data[campo]:
                    tokens = normalizar_e_tokenizar(str(data[campo]))
                    tokens_totais.extend(tokens)   

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
        print("Formato de arquivo não suportado. Use .txt ou .json")

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
# Calcular granlaridade entre dois conjuntos de tokens
# ---------------------------------------------
def granularidade(tokens_a, tokens_b):                                              # Granularidade entre dois conjuntos de tokens    
    if not tokens_a:                                                                # Se o conjunto A estiver vazio
        return 0                                                                    # Retorna 0 para evitar divisão por zero
    count_a = Counter(tokens_a)                                                     # Contador de tokens A
    count_b = Counter(tokens_b)                                                     # Contador de tokens B
    total = sum(count_a.values())                                                   # Total de tokens em A
    encontrados = sum(min(count_a[t], count_b.get(t,0)) for t in count_a)           # Tokens de A encontrados em B      
    return (encontrados / total) * 100                                              # Retorna a granularidade em porcentagem = (encontrados / total) * 100

# ---------------------------------------------
# MAIN
# ---------------------------------------------
def main():                                                                         # Função principal
    if len(sys.argv) < 3:                                                           # Verifica se possui pelo menos 2 argumentos (base + 1 cupom)
        print("Uso: python3 compare.py base.txt cupom1.txt cupom2.txt ...")         # Instruções de uso
        print("Aceita arquivos .txt (OCR) e .json")                                 # Instruções de uso
        return                                                                      # Encerra a função 

    base_path = sys.argv[1]                                                         # Caminho do arquivo base    
    base_nome = os.path.splitext(os.path.basename(base_path))[0]                    # Nome da base sem extensão e caminho
    base = extrair_tokens(base_path)                                                # Extrai tokens da base (função)
    print(f"Base '{base_nome}' carregada: {len(base)} tokens\n")                    # Mensagem de status
    cupons_paths = sys.argv[2:]                                                     # Caminhos dos arquivos de cupons a serem comparados      
    nomes_cupons = [os.path.splitext(os.path.basename(p))[0] for p in cupons_paths] # Nomes dos cupons sem extensão e caminho
    df_resultado = pd.DataFrame({"ITEM_BASE": base})                                # DataFrame para resultados (booleanos) 
    df_conteudo = pd.DataFrame({"ITEM_BASE": base})                                 # DataFrame para conteúdos encontrados 
    metricas_total = {}                                                             # Dicionário para armazenar métricas totais por cupom

    # Criar pasta para resultados e subpastas
    root_dir = "results"
    os.makedirs(root_dir, exist_ok=True)

    output_dir = os.path.join(root_dir, f"{base_nome}_results")         # Nome da pasta de resultados da detecção dentro de "results"    
    os.makedirs(output_dir, exist_ok=True)                              # Criação da pasta de resultados

    # ---------------------------------------------
    # Loop pelos cupons
    # ---------------------------------------------
    cupons_tokens = {}                                                  # Dicionário para armazenar tokens de cada cupom
    for path, nome in zip(cupons_paths, nomes_cupons):                  # Para cada caminho e nome de cupom em zip (lista paralela)
        cupom = extrair_tokens(path)                                    # Extrai tokens do cupom (função)
        cupons_tokens[nome] = cupom                                     # Armazena os tokens no dicionário
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
    
    # ABA 5 — GRÁFICO LONGO DE ACERTOS/ERROS + MATRIZ DE GRANULARIDADE   
    if len(base) > 0 and len(nomes_cupons) > 0:                         # Verificação antes de gerar o gráfico
        ws5 = wb.create_sheet("Grafico_Granularidade")                  # Quinta aba para gráfico        
        for i, nome in enumerate(nomes_cupons):                         # Para cada cupom analisado
            ws5.append([nome] + df_resultado[nome].astype(int).tolist())# Adiciona os dados do cupom (1 para True, 0 para false)        
        # -----------------------------
        # Criar matriz de granularidade
        # -----------------------------        
        df_gran = pd.DataFrame(index=nomes_cupons, columns=nomes_cupons, dtype=float)                       # DataFrame para armazenar a matriz de granularidade
        for i, n1 in enumerate(nomes_cupons):                                                               # Para cada cupom n1
            for j, n2 in enumerate(nomes_cupons):                                                           # Para cada cupom n2
                df_gran.loc[n1, n2] = granularidade(cupons_tokens[n1], cupons_tokens[n2])                   # Calcula a granularidade entre n1 e n2

        # Matriz simétrica para visualização (heatmap mais intuitivo)
        df_gran_sim = pd.DataFrame(index=nomes_cupons, columns=nomes_cupons, dtype=float)                   # DataFrame para matriz simétrica
        for n1 in nomes_cupons:                                                                             # Para cada cupom n1
            for n2 in nomes_cupons:                                                                         # Para cada cupom n2
                g1 = granularidade(cupons_tokens[n1], cupons_tokens[n2])                                    # Calculla a granularidade A em B
                g2 = granularidade(cupons_tokens[n2], cupons_tokens[n1])                                    # Calculla a granularidade B em A
                df_gran_sim.loc[n1, n2] = (g1 + g2)/2                                                       # Média das granularidades para simetria        

        ws5.append([])                                                                                      # linha em branco
        ws5.append(["Granularidade (%)"] + list(df_gran.columns))                                           # Cabeçaalho da matriz de granularidade 
        for idx, row in df_gran.iterrows():                                                                 # Para cada linha da matriz de granularidade 
            ws5.append([idx] + row.tolist())                                                                # Adiciona a linha na planilha

        plt.figure(figsize=(max(len(nomes_cupons)*0.8, 8), max(len(nomes_cupons)*0.5, 6)))                  # Figura do tamanho dinâmico baseado no número de cupons
        sns.heatmap(df_gran_sim, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label':'% Granularidade (simétrica)'})        
        plt.title(f"Matriz de Granularidade (A em B) - {base_nome}")                                        # Título do gráfico
        plt.xlabel("Comparado com")                                                                         # Mensagem do eixo X
        plt.ylabel("Base")                                                                                  # Mensagem do eixo Y
        plt.tight_layout()                                                                                  # Ajuste automático do layoult
        png_name = os.path.join(output_dir, f"granularidade_{base_nome}.png")                               # Nome do arquivo PNG de saída
        plt.savefig(png_name)                                                                               # Salva a figura como PNG
        plt.close()                                                                                         # Fecha a figura para liberar memória        
        print(f"\nMatriz de granularidade salva como PNG: {png_name}")                                        # Mensagem de status

        # -----------------------------
        # Gráfico longo de acertos/erros
        # -----------------------------
        itens_base = df_resultado["ITEM_BASE"].tolist()                             # Para o eixo X do gráfico
        x = range(len(itens_base))                                                  # Eixo X numérico com base no número de itens
        plt.figure(figsize=(max(len(itens_base)*0.4, 8), 6))                        # Figura maior para muitos itens, ajustando largura baseado em número de itens, altura fixa 
        offset = 0.03                                                               # distância entre linhas
        for i, nome in enumerate(nomes_cupons):                                     # Para cada cupom analisado
            y = df_resultado[nome].astype(int) + i*offset                           # Eixo Y com offset para visualização
            plt.plot(x, y, marker='o', label=nome)                                  # Plota a linha com marcadores
        
        plt.xticks(x, itens_base, rotation=90)                                      # Mostra os nomes dos itens na horizontal
        plt.xlabel("Item Base")                                                     # Rótulo do eixo X
        plt.ylabel("Acerto (1) / Erro (0)")                                         # Rótulo do eixo Y
        plt.title("Acertos e Erros por Cupom")                                      # Título do gráfico
        plt.legend(loc='best')                                                      # Legenda no melhor local de maneira autoamtica
        plt.tight_layout()                                                          # Ajuste automático do layoult
        plt.grid(True, linestyle='--', alpha=0.5)                                   # Adiciona grade ao gráfico
        plt.yticks([0, 1], ["Erro (0)", "Acerto (1)"])                              # Rótulos do eixo Y
        plt.ylim(-0.1, 1 + len(nomes_cupons)*offset + 0.1)                          # Limites do eixo Y    
        save_name = os.path.join(output_dir, f"grafico_comparacao_{base_nome}.png") # Nome do arquivo de saída a ser salvo
        plt.savefig(save_name)                                                      # Salva o gráfico como imagm        
        plt.close()                                                                 # Fecha a figura para liberar memória
        print(f"Gráfico salvo: {save_name}")                                        # Mensagem de status
    else:                                                                           # Se não há dados avisa
        print("AVISO: Não há dados suficientes para gerar o gráfico")               # Mensagem de aviso
    output_file = os.path.join(output_dir, f"comparacao_{base_nome}.xlsx")          # Salvar arquivo XLSX
    wb.save(output_file)                                                            # Salva o arquivo XLSX
    print(f"\nArquivo gerado: {output_file}")                                       # Mensagem de status
    
    if len(base) == 0:                                                                                                  # Verifica se a base está vazia
        print("\nAVISO: A base não contém tokens! Verifique o formato do arquivo.")                                     # Se estiver, avisa o usuário
        print("Para JSON, certifique-se que possui a estrutura: {\"itens\": [{\"codigo\": ..., \"descricao\": ...}]}")  # Se estiver, avisa o usuário#
        print("Para TXT, certifique-se que possui linhas no formato: OCR='...'")                                        # Se estiver, avisa o usuário

if __name__ == "__main__":  # Execução do main
    main()                  # Chama a função principal