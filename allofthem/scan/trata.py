import os
import cv2
import numpy as np
import imutils
from rembg import remove
import tkinter as tk
from tkinter import filedialog, messagebox

EXTENSOES = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")

PASTA_ENTRADA = os.getenv("PASTA_ENTRADA_TRATA", r"D:\img\SEM FUNDO")
PASTA_SAIDA = os.getenv("PASTA_SAIDA_TRATA", r"D:\img\TRATA")

# ==================================================
# FUNÇÕES AUXILIARES – PERSPECTIVA (IGUAL AO SEU)
# ==================================================

def ordenar_pontos(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def transformar_perspectiva(imagem, pts):
    rect = ordenar_pontos(pts)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(imagem, M, (maxWidth, maxHeight))

def executar_scanner(img_original):
    borda = 20
    img_padded = cv2.copyMakeBorder(
        img_original, borda, borda, borda, borda,
        cv2.BORDER_CONSTANT, value=[0, 0, 0]
    )

    gray = cv2.cvtColor(img_padded, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 60, 160)
    edged = cv2.dilate(edged, np.ones((5, 5), np.uint8), 1)

    conts = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    conts = imutils.grab_contours(conts)
    conts = sorted(conts, key=cv2.contourArea, reverse=True)[:5]

    for c in conts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.05 * peri, True)
        if len(approx) == 4:
            pts = approx.reshape(4, 2)
            pts = np.clip(pts - borda, 0, [img_original.shape[1], img_original.shape[0]])
            return transformar_perspectiva(img_original, pts)

    return img_original

# ==================================================
# MAIN
# ==================================================

def main():
    root = tk.Tk()
    root.withdraw()

    pasta_entrada = PASTA_ENTRADA#filedialog.askdirectory(title="Selecione a PASTA DE ENTRADA")
    if not pasta_entrada:
        return

    pasta_saida = PASTA_SAIDA#filedialog.askdirectory(title="Selecione a PASTA DE SAÍDA")
    if not pasta_saida:
        return

    pasta_sem_fundo = os.path.join(pasta_saida, "01_sem_fundo")
    pasta_persp = os.path.join(pasta_saida, "02_perspectiva")
    pasta_limiar = os.path.join(pasta_saida, "03_limiarizacao")

    os.makedirs(pasta_sem_fundo, exist_ok=True)
    os.makedirs(pasta_persp, exist_ok=True)
    os.makedirs(pasta_limiar, exist_ok=True)

    arquivos = [f for f in os.listdir(pasta_entrada) if f.lower().endswith(EXTENSOES)]

    if not arquivos:
        messagebox.showwarning("Aviso", "Nenhuma imagem encontrada.")
        return

    for nome in arquivos:
        print(f"Processando: {nome}")

        # -------------------------
        # 1. REMOVE FUNDO
        # -------------------------
        caminho_original = os.path.join(pasta_entrada, nome)
        with open(caminho_original, "rb") as f:
            img_bytes = f.read()

        img_sem_fundo = remove(img_bytes)
        nome_base = os.path.splitext(nome)[0]
        caminho_sf = os.path.join(pasta_sem_fundo, f"{nome_base}_sem_fundo.png")

        with open(caminho_sf, "wb") as f:
            f.write(img_sem_fundo)

        # -------------------------
        # 2. PERSPECTIVA
        # -------------------------
        img = cv2.imread(caminho_sf)
        img = imutils.resize(img, height=800)
        img_persp = executar_scanner(img)

        caminho_persp = os.path.join(pasta_persp, f"{nome_base}_perspectiva.png")
        cv2.imwrite(caminho_persp, img_persp)

        # -------------------------
        # 3. LIMIARIZAÇÃO (SEU PADRÃO)
        # -------------------------
        gray = cv2.cvtColor(img_persp, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 9
        )

        H, W = thresh.shape
        margem = 18
        final = thresh[margem:H - margem, margem:W - margem]

        caminho_final = os.path.join(pasta_limiar, f"{nome_base}_final.png")
        cv2.imwrite(caminho_final, final)

    messagebox.showinfo("Concluído", "Pipeline finalizado com sucesso!")

if __name__ == "__main__":
    main()
