from rembg import remove
from tkinter import Tk, filedialog, messagebox
import os
# rembg usando a rede u2net se mostrou mais eficaz para o uso do ocr

# Inicializa janela oculta
root = Tk()
root.withdraw()

# Escolher pasta de entrada
input_dir = filedialog.askdirectory(title="Selecione a pasta de entrada das imagens")
if not input_dir:
    messagebox.showinfo("Cancelado", "Nenhuma pasta de entrada foi selecionada.")
    exit()

# Escolher pasta de saída
output_dir = filedialog.askdirectory(title="Selecione a pasta de saída para salvar as imagens")
if not output_dir:
    messagebox.showinfo("Cancelado", "Nenhuma pasta de saída foi selecionada.")
    exit()

# Garante que a pasta de saída existe
os.makedirs(output_dir, exist_ok=True)

# Extensões aceitas
extensoes = (".png", ".jpg", ".jpeg", ".bmp", ".webp")

# Lista arquivos da pasta
arquivos = [f for f in os.listdir(input_dir) if f.lower().endswith(extensoes)]

if not arquivos:
    messagebox.showinfo("Aviso", "Nenhuma imagem encontrada na pasta selecionada.")
    exit()

# Processa cada imagem
for arquivo in arquivos:
    try:
        file_path = os.path.join(input_dir, arquivo)

        # Lê a imagem original
        with open(file_path, "rb") as input_file:
            input_data = input_file.read()

        # Remove fundo
        output_data = remove(input_data)

        # Define nome da nova imagem
        name_without_ext = os.path.splitext(arquivo)[0]
        output_path = os.path.join(output_dir, f"{name_without_ext}_sem_fundo.png")

        # Salva imagem processada
        with open(output_path, "wb") as output_file:
            output_file.write(output_data)

        print(f"✅ {arquivo} -> {output_path}")

    except Exception as e:
        print(f"❌ Erro ao processar {arquivo}: {str(e)}")

messagebox.showinfo("Concluído", f"Processamento finalizado!\nImagens salvas em:\n{output_dir}")