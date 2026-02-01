'''
Informações: Módulo de configuração para o PaddleGUI, incluindo definições de fonte personalizada, configurações do PaddleOCR e
funções auxiliares para cores de plotage,.
Dividido em: 
1 - Detecção de sistema operacional para definir a fonte correta a ser utilizada, caso contrário usa a fonte padrão do PIL
2 - Um modelo para detecção de texto
3 - Um modelo para reconhecer o que foi detectado
'''

import platform, re
import numpy as np
from PIL import ImageFont
from paddleocr import PaddleOCR
from sklearn.cluster import DBSCAN

# === Detectar o sistema operacional para definir o caminho da fonte a ser utilizada ===
system = platform.system()
match(system):
    case "Darwin":
        font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    case "Linux":
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    case "Windows":
        font_path = "C:/Windows/Fonts/arialbd.ttf"  
    case _:
        print("Sistema operacional não reconhecido. Usando fonte padrão do PIL.")
        font_path = None

# === Carregar a fonte personalizada para plotagem nas imagens baseado no Sistema Operacional ===
try:     
    font = ImageFont.truetype(font_path, size=40)
except:
    font = ImageFont.load_default()  # Se não encontrou a fonte, será utilizada a fonte padrão do PIL

# === Função para obter a fonte com tamanho dinâmico baseado no tamanho das bouding-boxes encontradas ===
def get_font(size=40):
    try:
        return ImageFont.truetype(font_path, size=size)
    except:        
        return ImageFont.load_default()

# === Configurações do PaddleOCR  ===
# OCR de detecção de texto, usado para localizar as áreas de texto na imagem
ocr_detector = PaddleOCR(
    use_dilation=False,
    ocr_version='PP-OCRv3',
    use_angle_cls=True,
    det_lang='pt',
    show_log=False,    
)

# OCR de reconhecimento de texto, usado para reconhecer o texto nas áreas detectadas
ocr_recognizer = PaddleOCR(
    use_dilation=False,
    ocr_version='PP-OCRv4',
    use_angle_cls=True,
    lang='pt',
    show_log=False,    
)

# === Função definição de cor para a plotagem baseado no score ===
def get_color(score=None):
    return (0, 255, 0) if score >= 0.80 else (255, 0, 0) # se for maior ou igual a 0.85 a cor será verde, caso contrário será vermelha    

# === Função para ordenar tokens extraídos do OCR deixando-os em ordem de leitura baseado nas coordenadas x e y ===

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

    return tokens


def reorder_tokens(tokens, verbose=False):
    """
    Ordena tokens em linhas usando clustering DBSCAN OTIMIZADO - 100% AUTOMÁTICO
    
    Estratégia: usa altura mínima dos tokens como referência para evitar
    juntar linhas distintas que estão próximas verticalmente.
    
    Args:
        tokens: Lista de dicionários com text, score, x, y, x2, y2
        verbose: Se True, imprime informações de debug
    
    Returns:
        Lista de linhas, onde cada linha é uma lista de tokens ordenados por x
    """
    if not tokens:
        return []
    
    # === PASSO 1: Calcular parâmetros adaptativos ===
    alturas = [abs(t["y2"] - t["y"]) for t in tokens]
    altura_min = np.min(alturas)
    altura_media = np.mean(alturas)
    altura_max = np.max(alturas)
    
    # Estratégia conservadora: usa altura mínima como base
    # Isso evita juntar linhas próximas mas distintas
    eps = altura_min * 0.8  # 80% da menor altura
    
    if verbose:
        print(f"[Clustering] Altura mínima: {altura_min:.2f}px")
        print(f"[Clustering] Altura média: {altura_media:.2f}px")
        print(f"[Clustering] Altura máxima: {altura_max:.2f}px")
        print(f"[Clustering] Eps calculado: {eps:.2f}px (conservador)")
    
    # === PASSO 2: Clustering nas coordenadas Y (vertical) ===
    y_coords = np.array([[t["y"]] for t in tokens])
    
    # DBSCAN com parâmetro conservador
    clustering = DBSCAN(eps=eps, min_samples=1, metric='euclidean').fit(y_coords)
    
    if verbose:
        n_clusters = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
        print(f"[Clustering] {n_clusters} linhas detectadas")
    
    # === PASSO 3: Agrupar tokens por cluster (linha) ===
    linhas_dict = {}
    for idx, label in enumerate(clustering.labels_):
        if label not in linhas_dict:
            linhas_dict[label] = []
        linhas_dict[label].append(tokens[idx])
    
    # === PASSO 4: Ordenar linhas de cima para baixo ===
    linhas = []
    for label in sorted(linhas_dict.keys(), key=lambda k: min(t["y"] for t in linhas_dict[k])):
        linha = linhas_dict[label]
        # Ordena tokens dentro da linha por X (esquerda para direita)
        linha.sort(key=lambda t: t["x"])
        linhas.append(linha)
    
    # === PASSO 5: Pós-processamento inteligente ===
    # Mescla APENAS se os tokens estiverem alinhados horizontalmente
    if len(linhas) > 1:
        linhas_merged = [linhas[0]]
        
        for i in range(1, len(linhas)):
            linha_prev = linhas_merged[-1]
            linha_curr = linhas[i]
            
            # Calcula Y médio de cada linha
            y_prev = np.mean([t["y"] for t in linha_prev])
            y_curr = np.mean([t["y"] for t in linha_curr])
            
            # Calcula sobreposição horizontal (X)
            x_prev_min = min(t["x"] for t in linha_prev)
            x_prev_max = max(t["x2"] for t in linha_prev)
            x_curr_min = min(t["x"] for t in linha_curr)
            x_curr_max = max(t["x2"] for t in linha_curr)
            
            # Há sobreposição horizontal?
            overlap = not (x_prev_max < x_curr_min or x_curr_max < x_prev_min)
            
            # Mescla APENAS se:
            # 1. Linhas estão muito próximas (< altura mínima)
            # 2. NÃO há sobreposição horizontal (estão lado a lado)
            if abs(y_curr - y_prev) < altura_min and not overlap:
                linhas_merged[-1].extend(linha_curr)
                linhas_merged[-1].sort(key=lambda t: t["x"])
            else:
                linhas_merged.append(linha_curr)
        
        linhas = linhas_merged
    
    if verbose:
        print(f"[Clustering] {len(linhas)} linhas finais")
        for i, linha in enumerate(linhas):
            textos = [t["text"] for t in linha]
            print(f"  Linha {i+1}: {' '.join(textos)}")
    
    return linhas