import re

def parse_ocr_txt(txt_file): #
    """
    Lê o txt salvo pelo OCR e retorna uma lista de dicionários:
    [
      {"text": "ARROZ", "score": 0.95, "x": 120, "y": 200},
      ...
    ]
    """
    pattern = r"OCR='(.*?)', score=([\d.]+), bbox=\[(\d+),(\d+),(\d+),(\d+)\]" # Regex para extrair texto, score e bounding box do .txt
    tokens = [] # Palavras extraidas

    with open(txt_file, "r", encoding="utf-8") as f: # Abrir arquivo txt apenas como leitura
        for line in f:
            match = re.search(pattern, line)
            if match:
                text = match.group(1).strip()     # Extrai o texto
                score = float(match.group(2))     # Extrai o score e converte para float
                x0 = int(match.group(3))          # coordenada x0
                y0 = int(match.group(4))          # coordenada y0
                x1 = int(match.group(5))          # coordenada x1
                y1 = int(match.group(6))          # coordenada y1

                tokens.append({                   # Informações extraidas adicionadas na lista de tokens
                    "text": text,                   
                    "score": score,
                    "x": x0,
                    "y": y0,
                    "x2": x1,
                    "y2": y1
                })

    return tokens                                 # Retorna os tokens do arquivo txt


def reorder_tokens(tokens, line_threshold=5):
    """
    Ordena palavras por coordenadas:
    1. Ordena por y (vertical)
    2. Dentro da linha, ordena por x (horizontal)
    3. Agrupa por linhas usando tolerância
    """
    tokens = sorted(tokens, key=lambda t: (t["y"], t["x"]))     # Ordena tokens baseado em y e x

    linhas = []
    linha_atual = []
    last_y = None

    for token in tokens:                                                 # Percorre todos os tokens 
        if last_y is None or abs(token["y"] - last_y) <= line_threshold: # Se a diferença do y atual com o último for menor que o valor do threshold
            linha_atual.append(token)  # adiciona o token na linha atual
        else:
            linhas.append(linha_atual) # aduciona a linha atual na lista de linhas   
            linha_atual = [token]      # inicia uma nova linha atual com o token atual
        last_y = token["y"]            # Atualiza o last_y com o y do token atual

    if linha_atual:                    # Após o loop, se houver tokens na linha atual   
        linhas.append(linha_atual)     # adiciona a linha atual na lista de linhas 

    # Ordena dentro das linhas por X
    for linha in linhas:
        linha.sort(key=lambda t: t["x"])

    return linhas                      # Retorna as linhas ordenadas baseado no threshold definido