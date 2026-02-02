import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox

def main():
    # ==========================================
    # JANELA TKINTER (INVISÍVEL)
    # ==========================================
    root = tk.Tk()
    root.withdraw()

    # ==========================================
    # SELECIONAR PASTA DE ENTRADA
    # ==========================================
    pasta_entrada = filedialog.askdirectory(title="Selecione a pasta de ENTRADA (imagens)")
    if not pasta_entrada:
        return

    # ==========================================
    # SELECIONAR PASTA DE SAÍDA
    # ==========================================
    pasta_saida = filedialog.askdirectory(title="Selecione a pasta de SAÍDA")
    if not pasta_saida:
        return

    os.makedirs(pasta_saida, exist_ok=True)

    extensoes = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")

    arquivos = [
        f for f in os.listdir(pasta_entrada)
        if f.lower().endswith(extensoes)
    ]

    if not arquivos:
        messagebox.showwarning("Aviso", "Nenhuma imagem encontrada na pasta.")
        return

    # ==========================================
    # PROCESSAMENTO EM LOTE (ORIGINAL)
    # ==========================================
    for arquivo in arquivos:
        caminho = os.path.join(pasta_entrada, arquivo)
        print(f"Processando: {arquivo}")

        transform = cv2.imread(caminho)
        if transform is None:
            print("Erro ao ler imagem.")
            continue

        # ==========================================
        # CÓDIGO ORIGINAL 
        # ==========================================

        img_process = cv2.cvtColor(transform, cv2.COLOR_BGR2GRAY)

        img_process = cv2.adaptiveThreshold(
            img_process,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            9
        )

        H, W = img_process.shape
        margem = 18
        img_final = img_process[margem:H - margem, margem:W - margem]

        nome_base, ext = os.path.splitext(arquivo)
        novo_nome = f"{nome_base}_limiarizada{ext}"
        caminho_salvar = os.path.join(pasta_saida, novo_nome)

        cv2.imwrite(caminho_salvar, img_final)

    messagebox.showinfo(
        "Concluído",
        f"Processamento finalizado!\nImagens salvas em:\n{pasta_saida}"
    )

if __name__ == "__main__":
    main()
