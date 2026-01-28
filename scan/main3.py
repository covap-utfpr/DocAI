import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox

# ==========================================
# CONFIGURAÇÕES (AJUSTADAS)
# ==========================================

PASTA_ENTRADA = r"D:\img\SEM FUNDO"
PASTA_SAIDA = r"D:\img\TRATA"

os.makedirs(PASTA_SAIDA, exist_ok=True)

EXTENSOES_VALIDAS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")

# ==========================================
# MAIN – PROCESSAMENTO EM LOTE
# ==========================================

def main():
    root = tk.Tk()
    root.withdraw()

    arquivos = [
        f for f in os.listdir(PASTA_ENTRADA)
        if f.lower().endswith(EXTENSOES_VALIDAS)
    ]

    if not arquivos:
        messagebox.showwarning("Aviso", "Nenhuma imagem encontrada na pasta de entrada.")
        return

    for nome in arquivos:
        caminho = os.path.join(PASTA_ENTRADA, nome)
        print(f"Processando: {nome}")

        img = cv2.imread(caminho)
        if img is None:
            print("Erro ao abrir imagem.")
            continue

        # ==========================================
        # 1. ESCALA DE CINZA
        # ==========================================
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # ==========================================
        # MELHORIA 1: SHARPENING
        # ==========================================
        kernel_sharpening = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        sharp = cv2.filter2D(gray, -1, kernel_sharpening)

        # ==========================================
        # MELHORIA 2: THRESHOLD ADAPTATIVO
        # ==========================================
        scan_pro = cv2.adaptiveThreshold(
            sharp, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            21, 10
        )

        # ==========================================
        # MELHORIA 3: LIMPEZA DE RUÍDO
        # ==========================================
        scan_limpo = cv2.medianBlur(scan_pro, 3)

        # ==========================================
        # SALVAR RESULTADO
        # ==========================================
        nome_base, ext = os.path.splitext(nome)
        novo_nome = f"{nome_base}_PRO{ext}"
        caminho_salvar = os.path.join(PASTA_SAIDA, novo_nome)

        cv2.imwrite(caminho_salvar, scan_limpo)

    messagebox.showinfo(
        "Scanner Pro",
        "Processamento concluído.\n\nTodas as imagens foram tratadas e salvas."
    )

if __name__ == "__main__":
    main()
