import os
import cv2
import numpy as np
import imutils
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURAÇÕES
# ==========================================
PASTA_SAIDA = r"D:\img\TRATA"
os.makedirs(PASTA_SAIDA, exist_ok=True)

# ==========================================
# FUNÇÃO PARA MOSTRAR IMAGENS (MATPLOTLIB)
# ==========================================
def mostrar(imagem, titulo="Imagem"):
    plt.figure(figsize=(6, 8))

    if len(imagem.shape) == 2:
        plt.imshow(imagem, cmap="gray")
    else:
        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        plt.imshow(imagem_rgb)

    plt.title(titulo)
    plt.axis("off")
    plt.show()

# ==========================================
# JANELA PARA SELECIONAR IMAGEM
# ==========================================
def selecionar_imagem():
    root = tk.Tk()
    root.withdraw()

    caminho = filedialog.askopenfilename(
        title="Selecione a imagem",
        filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )

    if not caminho:
        messagebox.showwarning("Aviso", "Nenhuma imagem selecionada.")
        return None

    return caminho

# ==========================================
# DETECÇÃO DE CONTORNOS
# ==========================================
def encontrar_contornos(img):
    conts = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    conts = imutils.grab_contours(conts)
    conts = sorted(conts, key=cv2.contourArea, reverse=True)[:6]
    return conts

# ==========================================
# ORDENAÇÃO DOS PONTOS
# ==========================================
def ordenar_pontos(pontos):
    pontos = pontos.reshape((4, 2))
    pontos_novos = np.zeros((4, 1, 2), dtype=np.int32)

    soma = pontos.sum(axis=1)
    pontos_novos[0] = pontos[np.argmin(soma)]   # topo esquerdo
    pontos_novos[2] = pontos[np.argmax(soma)]   # baixo direito

    diferenca = np.diff(pontos, axis=1)
    pontos_novos[1] = pontos[np.argmin(diferenca)]  # topo direito
    pontos_novos[3] = pontos[np.argmax(diferenca)]  # baixo esquerdo

    return pontos_novos

# ==========================================
# PROCESSAMENTO PRINCIPAL
# ==========================================
def main():
    caminho_imagem = selecionar_imagem()
    if caminho_imagem is None:
        return

    img = cv2.imread(caminho_imagem)
    if img is None:
        messagebox.showerror("Erro", "Erro ao carregar imagem.")
        return

    original = img.copy()

    (H, W) = img.shape[:2]
    print(f"Altura: {H} | Largura: {W}")

    mostrar(img, "Imagem Original")

    # ==========================================
    # 1. GRAYSCALE
    # ==========================================
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mostrar(gray, "Escala de Cinza")

    # ==========================================
    # 2. GAUSSIAN BLUR
    # ==========================================
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    mostrar(blur, "Gaussian Blur")

    # ==========================================
    # 3. CANNY (BORDAS)
    # ==========================================
    edged = cv2.Canny(blur, 60, 160)

    # Cria um "pincel" quadrado de 5x5 pixels
    kernel = np.ones((6, 6), np.uint8)
    # Aplica a dilatação para engrossar as bordas brancas
    edged = cv2.dilate(edged, kernel, iterations=1)
    # --------------------------

    mostrar(edged, "Detecção de Bordas")

    # ==========================================
    # 4. CONTORNOS
    # ==========================================
    contornos = encontrar_contornos(edged.copy())

    maior = None
    max_area = 0

    for c in contornos:
        perimetro = cv2.arcLength(c, True)
        # Aumentei um pouco a tolerância de 0.02 para 0.04
        # Isso força o algoritmo a simplificar mais a forma
        #aproximacao = cv2.approxPolyDP(c, 0.04 * perimetro, True)
        # Tente 0.04 ou 0.05 se 0.02 não estiver funcionando
        aproximacao = cv2.approxPolyDP(c, 0.05 * perimetro, True)
        # Se tiver 4 pontos, ótimo.
        if len(aproximacao) == 4:
            maior = aproximacao
            break
    # ==========================================
    # 5. DESENHO DO CONTORNO
    # ==========================================
    cv2.drawContours(img, [maior], -1, (0, 255, 0), 3)
    mostrar(img, "Documento Detectado")

    # ==========================================
    # 6. ORDENAÇÃO DOS PONTOS
    # ==========================================
    pontos_ordenados = ordenar_pontos(maior)
    print("Pontos ordenados:")
    print(pontos_ordenados)

    # ==========================================
    # SALVAR RESULTADO
    # ==========================================
    nome = os.path.basename(caminho_imagem)
    saida = os.path.join(PASTA_SAIDA, f"detectado_{nome}")
    cv2.imwrite(saida, img)

    messagebox.showinfo("Sucesso", f"Resultado salvo em:\n{saida}")

# ==========================================
# EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    main()