import os
import cv2
import numpy as np
import imutils
import tkinter as tk
from tkinter import messagebox

# ==========================================
# CONFIGURAÇÕES
# ==========================================

PASTA_ENTRADA = r"D:\img\SEM FUNDO"
PASTA_SAIDA = r"D:\img\TRATA"

os.makedirs(PASTA_SAIDA, exist_ok=True)

EXTENSOES_VALIDAS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")

# ==========================================
# 1. FUNÇÕES MATEMÁTICAS
# ==========================================

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

# ==========================================
# 2. AS TRÊS TÉCNICAS
# ==========================================

def tecnica_1_contornos(edged, area_minima):
    conts = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    conts = imutils.grab_contours(conts)
    conts = sorted(conts, key=cv2.contourArea, reverse=True)[:5]

    for c in conts:
        if cv2.contourArea(c) < area_minima:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.05 * peri, True)
        if len(approx) == 4:
            return approx.reshape(4, 2)
    return None

def tecnica_2_hough(edged):
    linhas = cv2.HoughLinesP(
        edged, 1, np.pi / 180,
        threshold=80, minLineLength=100, maxLineGap=40
    )
    pontos = []
    if linhas is not None:
        for linha in linhas:
            x1, y1, x2, y2 = linha[0]
            pontos.extend([(x1, y1), (x2, y2)])

        if pontos:
            pontos = np.array(pontos)
            x, y, w, h = cv2.boundingRect(pontos)
            return np.array(
                [[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
                dtype="float32"
            )
    return None

def tecnica_3_minarea(edged, area_minima, area_maxima):
    conts, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts = sorted(conts, key=cv2.contourArea, reverse=True)[:5]

    for c in conts:
        area = cv2.contourArea(c)
        if area < area_minima or area > area_maxima:
            continue
        rect = cv2.minAreaRect(c)
        return np.int64(cv2.boxPoints(rect))
    return None

# ==========================================
# 3. SCANNER
# ==========================================

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

    area_total = img_padded.shape[0] * img_padded.shape[1]

    t1 = tecnica_1_contornos(edged, area_total * 0.05)
    t3 = tecnica_3_minarea(edged, area_total * 0.05, area_total * 0.99)
    t2 = tecnica_2_hough(edged)

    vencedor = None
    if t1 is not None:
        vencedor = t1
    elif t3 is not None:
        vencedor = t3
    elif t2 is not None:
        vencedor = t2

    if vencedor is None:
        return None

    pts_reais = np.clip(
        vencedor.astype(float) - borda,
        0,
        [img_original.shape[1], img_original.shape[0]]
    )

    return transformar_perspectiva(img_original, pts_reais)

# ==========================================
# MAIN – PROCESSAMENTO EM LOTE
# ==========================================

def main():
    arquivos = [
        f for f in os.listdir(PASTA_ENTRADA)
        if f.lower().endswith(EXTENSOES_VALIDAS)
    ]

    if not arquivos:
        messagebox.showwarning("Aviso", "Nenhuma imagem encontrada.")
        return

    for nome in arquivos:
        caminho = os.path.join(PASTA_ENTRADA, nome)
        print(f"Processando: {nome}")

        img = cv2.imread(caminho)
        if img is None:
            print("Erro ao abrir imagem.")
            continue

        img_resized = imutils.resize(img, height=800)
        resultado = executar_scanner(img_resized)

        if resultado is not None:
            nome_saida = os.path.splitext(nome)[0] + "_perspectiva.png"
            cv2.imwrite(os.path.join(PASTA_SAIDA, nome_saida), resultado)

    messagebox.showinfo("Concluído", "Processamento finalizado.")

if __name__ == "__main__":
    main()
