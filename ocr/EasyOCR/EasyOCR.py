import glob
import os
import sys
import easyocr
import cv2
import numpy as np
import easygui
import Modules.config as config
import Modules.path as path 
from PIL import Image, ImageDraw, ImageFont
from matplotlib import pyplot as plt
from Modules.json_processing import clear_data, to_json, create_json, save_json

# === Pasta de resultados ===
RESULT_DIR = path.results

# === Caminho padrão do EasyGUI ===
load_path = path.load_images

# === Menu de ajuda ===
def help_menu():
    print("""
    EasyOCR — Ferramenta de extração de texto de imagens por via de comando ou por interface gráfica.

    Uso:
        python3 EasyOCR.py [imagem|diretório]    
        python3 EasyOCR.py --help

    Exemplos:
        python3 EasyOCR.py
        python3 EasyOCR.py foto.jpg
        python3 EasyOCR.py pasta/
    """)
    exit()

# === Função principal de OCR ===
def process_image(img_path, its_console=False):

    img_name = os.path.basename(img_path)
    name_no_ext = os.path.splitext(img_name)[0]

    # Carrega OCR com base nos dicionarios de lingua portuguesa e inglesa
    reader = easyocr.Reader(['pt', 'en'])

    try:
        result = reader.readtext(img_path, detail=1)
    except Exception as e:
        print(f"[ERRO] Falha no EasyOCR: {e}")
        return

    # Carrega imagem para desenhar com PIL
    img_cv = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(img_pil)

    # Fonte
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 22)

    # Arquivo TXT
    txt_output = os.path.join(RESULT_DIR, f"{name_no_ext}_EasyOCR.txt")
    raw_text = ""

    with open(txt_output, "w", encoding="utf-8") as f_txt:

        for bbox, text, score in result:
            x0 = int(bbox[0][0])
            y0 = int(bbox[0][1])
            x1 = int(bbox[2][0])
            y1 = int(bbox[2][1])

            # Linha estilo Paddle (foi a referencia para esta implementação)
            line = f"OCR='{text}', score={score:.2f}, bbox=[{x0},{y0},{x1},{y1}]\n"

            f_txt.write(line)
            raw_text += line

            # Desenhar retângulo baseado na pontuação de score.
            if score >= 0.85:
                draw.rectangle([x0, y0, x1, y1], outline=(0, 255, 0), width=3)
            else:
                draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=3)

            # Texto acima do box
            draw.text((x0, y0 - 28), text, fill=(255, 255, 255), font=font, stroke_width=1, stroke_fill=(0,0,0))

    # Imagem final
    plot_output = os.path.join(RESULT_DIR, f"{name_no_ext}_EasyOCR_plotagem.png")
    img_pil.save(plot_output)

    tokens = config.parse_ocr_txt(txt_output) # Parse para extrair os tokens do arquivo txt
    linhas = config.reorder_tokens(tokens)    # Reordena os tokens baseado na posição Y para formar linhas ordenadas
            
    clear_data()  # Garantir JSON limpo
    for linha in linhas:
        palavras_linha = [t["text"] for t in linha]
        to_json(palavras_linha)  
    create_json()
    save_json(filename=name_no_ext, output_dir=RESULT_DIR)

    print(f"[OK] TXT salvo em:      {os.path.abspath(txt_output)}")
    print(f"[OK] Imagem salva em:   {os.path.abspath(plot_output)}")

    # Se o processamento não for via console, mostra a imagem plotada
    if not its_console:
        plt.figure(figsize=(12, 16))
        plt.imshow(img_pil)
        plt.title(f"OCR: {img_name}")
        plt.axis("off")
        plt.show()

# === Carregar imagens do sistema ===
def load_image(img_paths, its_console):
    print(f"[INFO] Processando {len(img_paths)} imagem(ns)...")

    for img in img_paths:
        print(f"\n[PROCESSANDO] {img}")
        process_image(img, its_console)

# === MAIN ===
def main():

    args = sys.argv[1:]
    # se um argumento for --help ou -h, mostra o menu de ajuda
    if '--help' in args or '-h' in args:
        help_menu()

    # === Há argumentos? ===
    if args:
        img_paths = []
        its_console = True

        for arg in args:
            if os.path.isdir(arg):
                exts = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tif", "*.tiff", "*.webp")
                for ext in exts:
                    img_paths.extend(glob.glob(os.path.join(arg, ext)))
            else:
                img_paths.append(arg)

    # === Sem argumentos → EasyGUI ===
    else:
        its_console = False
        img_paths = easygui.fileopenbox(
            default=f"{load_path}/*",
            multiple=True,
            title="Selecione uma ou mais imagens (EasyOCR)"
        )

    if not img_paths:
        print("Nenhuma imagem selecionada.")
        exit()
    
    load_image(img_paths, its_console)

# ============================================================
if __name__ == "__main__":
    main()