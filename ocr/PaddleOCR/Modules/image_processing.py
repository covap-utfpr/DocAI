import os, cv2, time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from multiprocessing import Pool, cpu_count

# Importação dos módulos path, config, módulos das funções de JSON e corretor ortográfico
import Modules.path as path
import Modules.config as config
from Modules.json_processing import clear_data, to_json, create_json, save_json
from Modules.spellchecker import to_spellchecker as correct_word
from Modules.config import parse_ocr_txt, reorder_tokens 

its_console = False    # Variável para detectar se a entrada é via console ou EasyGUI
spellcorrector = True  # Variável para ativaar/desativar o corrector ortográfico pelo terminal através do argumento --nsc       
jsonoutput = True      # Variável para ativar/desativar a saída em JSON                                                     

# Função para carregar todas as imagens de um diretório pelo EasyGUI
def load_image(img_paths):
    start_time = time.time()

    print(f"[Info] Processando {len(img_paths)} imagem(ns)")

#    with Pool(cpu_count()) as pool:
#        pool.map(process_image, img_paths)
   
    for img_path in img_paths:
        process_image(img_path)

    end_time = time.time()

    print("----------------------------------------")
    elapsed = end_time - start_time
    if elapsed > 60:
        print(f"[Info] Tempo total: {elapsed / 60:.2f} minutos")
    else:
        print(f"[Info] Tempo total: {elapsed:.2f} segundos")

# Função para processar a imagem e aplicar OCR
def process_image(img_path):    
    start = time.time()
    print(f"Paddle Processando: file://{os.path.abspath(img_path)}")
    img_name = os.path.basename(img_path)         # Nome base do arquivo a ser feito o processamento de imagem
    name_no_ext = os.path.splitext(img_name)[0]   # Remove a extensão do nome do arquivo para uso posterior 

    # === Lê a imagem com OpenCV e converte para PIL ===
    img_cv = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(img_pil)

    # === OCR utilizando as configurações do modulo config ===
    det_output = config.ocr_detector.ocr(img_path, cls=True)   # Detecção de texto pelo módulo de detecção na config.py

    if not det_output or det_output[0] is None:
        print(f"[Aviso] Nenhuma detecção em: {img_path}")
        return

    det_res = det_output[0]
    result = []

    # Limpeza do JSON anterior
    if jsonoutput == True:
        clear_data()

    for box, _ in det_res:
        pts = np.array(box).astype(int)
        
        x0 = max(min(pts[:, 0]), 0)
        y0 = max(min(pts[:, 1]), 0)
        x1 = max(pts[:, 0])
        y1 = max(pts[:, 1])

        crop = img_rgb[y0:y1, x0:x1]  # recorta a região do texto
        crop_pil = Image.fromarray(crop)

        # Agora reconhece só esse crop
        rec_res = config.ocr_recognizer.ocr(np.array(crop_pil), det=False, rec=True, cls=True)[0]

        if rec_res:
            result.append((box, rec_res[0]))  # mantém compatível com o loop original

    # === Processa OCR e desenha ===
    raw_text = ""

    # Itera sobre os resultados do OCR
    for box, (text, score) in result:
        pts = np.array(box).astype(int)

        # Define os pontos extremos da caixa delimitadora 
        x0 = min(pts[0][0], pts[2][0])
        y0 = min(pts[0][1], pts[2][1])
        x1 = max(pts[0][0], pts[2][0])
        y1 = max(pts[0][1], pts[2][1])

        top_left = (x0, y0)                     # Topo superior esquerdo da caixa delimitadora
        bottom_right = (x1, y1)                 # Canto inferior direito da caixa delimitadora

        # CORRETOR ORTOGRAFICO VAI AQUI
        if spellcorrector == True:
            text, score = correct_word(text, score)               # Corrige a palavra utilizando o corretor ortográfico

        # Processamento JSON      
        #if jsonoutput == True:  
        #    to_json(text)                           # Processa o texto para identificar CPFs, CNPJs, datas, etc.           

        color = config.get_color(score)         # Desenha a caixa delimitadora do texto baseada no score do PaddleOCR

        draw.rectangle([top_left, bottom_right], outline=color, width=3) # Desenha a caixa delimitadora do texto para evitar sobreposiçaõ

        box_height = bottom_right[1] - top_left[1]  # Define dinamicamente o tamanho da fonte com base na altura da caixa
        font_size = max(10, int(box_height * 0.5))  # 50% da altura da caixa para garantir que o texto caiba na plotagem 
        font = config.get_font(size=font_size)      # Definição do tamanho da fonte baseado na altura da caixa 

        bbox = font.getbbox(text)                   # Obtém a caixa delimitadora do texto para calcular o tamanho do texto
        text_width = bbox[2] - bbox[0]              # Definição da largura do texto  
        text_height = bbox[3] - bbox[1]             # Definição da altuira do texto 

        text_x = top_left[0]                        # Posição X do texto, alinhado à esquerda da caixa delimitadora
        text_y = top_left[1] - text_height - 2      # Posição Y do texto, acima da caixa delimitadora 
        
        if text_y < 0:                              # Se o texto subir demais (sair da imagem), joga pra baixo da caixa
            text_y = bottom_right[1] + 2            # Desenha logo abaixo da caixa
        
        if text_x + text_width > img_pil.width:     # Se ultrapassar a borda direita, ajusta para caber 
            text_x = img_pil.width - text_width - 2 
        
        if text_x < 0:                              # Se ultrapassar a borda esquerda, ajusta para cab er
            text_x = 2

        # Contorno preto no texto para garantir melhor legibilidade
        for dx in [-1, 1]:                                                                      
            for dy in [-1, 1]:
                draw.text((text_x + dx, text_y + dy), text, font=font, fill=(0, 0, 0))

        # Texto principal branco 
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

        # A saída do OCR é formatada para incluir o texto identificado, o score baseado na confiança do Paddle e as coordenadas do bounding box
        raw_text += f"OCR='{text}', score={score:.2f}, bbox=[{x0},{y0},{x1},{y1}]\n"

    # Construção do JSON                                              
    if jsonoutput == True:
        create_json()   # Primeiro cria o JSON
        if spellcorrector == True:
            txt_filename = os.path.join(path.results, f"{name_no_ext}_Paddle_ocr_SpellCorrected.txt")
            plot_filename = os.path.join(path.results, f"{name_no_ext}_Paddle_plotagem_SpellCorrected.png")
            name = f"{name_no_ext}_PaddleOCR_JsonProcessing_SpellCorrected"
           # save_json(filename=f"{name_no_ext}_JsonProcessing_SpellCorrected", output_dir=path.results) # Salva o JSON no diretório de resultados com correção ortográfica
        else:        
            txt_filename = os.path.join(path.results, f"{name_no_ext}_Paddle_ocr_NoSpellCorrected.txt")
            plot_filename = os.path.join(path.results, f"{name_no_ext}_Paddle_plotagem_NoSpellCorrected.png")
            name = f"{name_no_ext}_Paddle_JsonProcessing_NoSpellCorrected"
           # save_json(filename=f"{name_no_ext}_JsonProcessing_NoSpellCorrected", output_dir=path.results)  # Salva o JSON no diretório de resultados sem correção ortográfica
    else:
        if spellcorrector == True:
            txt_filename = os.path.join(path.results, f"{name_no_ext}_Paddle_ocr_SpellCorrected.txt")
            plot_filename = os.path.join(path.results, f"{name_no_ext}_Paddle_plotagem_SpellCorrected.png")
            print("[Info] O módulo de json foi desabilitado")
        else:        
            txt_filename = os.path.join(path.results, f"{name_no_ext}_Paddle_ocr_NoSpellCorrected.txt")
            plot_filename = os.path.join(path.results, f"{name_no_ext}_Paddle_plotagem_NoSpellCorrected.png")
            print("[Info] O módulo de json foi desabilitado")

    # === Legenda na imagem ===
    caption_texts = [
        ("Verde: Texto CORRETO (match com esperado)", (0, 255, 0)),
        ("Vermelho: Texto ERRADO (não bate com esperado)", (255, 0, 0))
    ]

    # Posição base da legenda na imagem
    lx, ly = 20, img_pil.height - 100

    # Dssenha a legenda na imagem 
    for i, (caption, color) in enumerate(caption_texts):
        draw.text((lx, ly + i * 30), caption, fill=color, font=font)

    # === Salva os resultados em txt e imagem plotada ===
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(raw_text)    
        print(f"txt gravado, local: file://{os.path.abspath(txt_filename)}")
    img_pil.save(plot_filename)    
        
    # # EM TESTES: Depois de salvar o txt:
    if jsonoutput == True:
        tokens = parse_ocr_txt(txt_filename)
        linhas = reorder_tokens(tokens)
        
        # Agora enviamos na ORDEM CORRETA para o processamento JSON
        if jsonoutput:
            clear_data()  # Garantir JSON limpo
            for linha in linhas:
                palavras_linha = [t["text"] for t in linha]
                to_json(palavras_linha)  # Agora processa em lote corretamente
            create_json()
            save_json(filename=name, output_dir=path.results)


    # === Exibe com Matplotlib ===
    img_with_plot = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)  #Converte de RGB para BGR para compatibilidade com OpenCV
    plt.figure(figsize=(12, 16))                                        # Tamanho maior para melhor visualização  
    plt.imshow(cv2.cvtColor(img_with_plot, cv2.COLOR_BGR2RGB))          # Converte de BGR para RGB para garantir a exibição das cores do Matplotlib
    plt.axis("off")                                                     # Desativa os eixos para uma visualização mais limpa
    plt.title(f"OCR: {img_name}")                                       # Titulo da imagem com o nome do arquivo 
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)               # Preenche toda a figura
    
    if its_console == False:  # Se não for via console, exibe a imagem plotada
        plt.show()            # Opção para exibir a imagem plotada após o processamento, desativado para ser mais rapido            
    print(f"Paddle Identificou: file://{os.path.abspath(plot_filename)}") # Exibe o caminho da imagem plotada pelo PaddleOCR        
    end = time.time()
    print(f"[Info] {os.path.basename(img_path)} processada em {end - start:.2f} s")
