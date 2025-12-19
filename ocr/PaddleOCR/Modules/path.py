'''' 
Informações: Módulo path.py para gerenciar caminhos de entrada e saída de arquivos no projeto, podendo ser customizado conforme desejado.
'''

from pathlib import Path    # Unica importação necessária para manipulação de caminhos 

# Caminho base: diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent  

# Caminho onde os resultados obtidos serão salvos (relativo ao diretório do projeto)
results = BASE_DIR / "results_OCR"

# Caminho para as imagens a serem carregadas, caso não seja especificado como argumento 
load_images = BASE_DIR / "images"

# Cria os diretórios se não existirem
results.mkdir(parents=True, exist_ok=True)
load_images.mkdir(parents=True, exist_ok=True)

# Converter para string para garantir a compatibilidade com outros módulos do projeto
results = str(results)
load_images = str(load_images)