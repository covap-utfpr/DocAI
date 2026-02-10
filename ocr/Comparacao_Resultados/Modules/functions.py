import os
import re
import json
from collections import Counter

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
            lista_itens = data.get("itens") or data.get("item")
            if isinstance(lista_itens, list):
                for item in lista_itens:                        
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


# Rotular nomes
def rotular_nome(path):
    nome, ext = os.path.splitext(os.path.basename(path))
    ext = ext.lower()
    if ext == ".txt":
        return f"[TXT] {nome}"
    elif ext == ".json":
        return f"[JSON] {nome}"
    else:
        return f"[OUTRO] {nome}"