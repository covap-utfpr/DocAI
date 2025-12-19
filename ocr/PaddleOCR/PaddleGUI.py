''' 
Informações: PaddleGUI é o script principal para processamento de imagens utilizando o PaddleOCR + plotagem do Matplotlib + corretores ortográficos e saída JSON. 
O ciclo envolve: 
1 - selecionar uma imagem por argumento ou através do EasyGUI 
2 - identificar e reconhecer o texto na imagem utilizando módulo para detecção e reconhecimento
3 - aplicar corretoor ortográfico (pode ser desativado pelo argumento --nsc)
4 - processamento na imagem com plotagem pelo Matplotlib (com texto reconhecido e corrigido caso necessário)
5 - salva os resultados em .txt, imagem plotada e JSON com os resultaodos do OCR, dentro de Results_OCR
'''

# === Importações de bibliotecas e módulos necessários ===
import easygui, sys, os, glob                   # Bibliotecas necessárias para o script PaddleGUI.py
import Modules.path as path                     # Módulo path para gerenciar entrada e saída de arquivos

# === Caminho resultado e carregamento de imagens obtidos ===
result_path = path.results      # Caminho onde os resultados serão salvos, definidos no path.py
load_path =  path.load_images   # Caminho onde os arquivos de entrada pelo EasyGUI serão carregados, definidos no path.py

# === Menu de ajuda para o usuário ===
def help():
    print("""
    PaddleGUI - Projeto integrando PaddleOCR, Matplotlib, Corretores Ortográficos e saída JSON para um fluxo completo de OCR.
    
    Projeto em desenvolvimento pelo grupo de Computação Visual Aplicada (COVAP) da Universidade Tecnológica Federal do Paraná (UTFPR).          
    Site:   https://covap-utfpr.github.io/ 
    GitHub: https://github.com/covap-utfpr
          
    Uso: 
        python3.12 PaddleGUI.py [caminho_imagem_ou_diretório] [opções]\n
    Opções:
      --nospell        Desativa o corretor ortográfico.
      --nojson         Desativa o módulo de processamento de json
      --disable-all    Desativa todas as opções acima.
          
    Exemplos:
        python3.12 PaddleGUI.py                         # Utiliza o EasyGUI para selecionar imagens e com feedback em imagens plotadas (segure ctrl para selecionar multiplas imagens)
        python3.12 PaddleGUI.py image.jpg               # Processa uma imagem
        python3.12 PaddleGUI.py images/                 # Processa todas as imagens em um diretório
        python3.12 PaddleGUI.py image2.jpg --nospell    # Processa uma imagem sem corretor ortográfico [no spellchecker]
        python3.12 PaddleGUI.py image3.jpg --nojson     # Processa uma imagem sem saída em JSON [no json]        
        python3.12 PaddleGUI.py images/ --disable-all   # Processa todas as imagens em um diretório sem corretor ortográfico e sem json
        python3.12 PaddleGUI.py --help                  # Exibe este menu de ajuda
          """)
    exit()                              # Sai do programa após exibir a ajuda    

# === Importação preguiçosa do módulo image_processing para evitar problemas com multiprocessing, devido aos componentes do OCR ===
def lazy_import_image_processing():
    import Modules.image_processing as img_proc
    return img_proc

# === Função principal do script PaddleGUI.py ===
def main():                     
    args = sys.argv[1:]                     # Obtém argumentos da linha de comando
   
    if '--help' in args or '-h' in args:    # Informações de ajuda sobre os argumentos disponiveis
           help()
           return
    try:                   
        img_proc = lazy_import_image_processing()   # Seleciona imagens ou por argumento (imagem ou diretório) ou pelo processo do EasyGUI

        if '--disable-all' in args:                 # O argumento --disable-all desativa todos os itens anteriores e remove o argumento da lista. Prioridade maior
            img_proc.spellcorrector = False     
            img_proc.jsonoutput = False            
            args.remove('--disable-all')
        else:
            if '--nospell' in args:                 # O argumento --nospell (no spellchecker) desativa o corretor ortográfico e remove o argumento da lista
                img_proc.spellcorrector = False     
                args.remove('--nospell')                        
            elif '--nojson' in args:                # O argumento --nojson desativa a saída em JSON e remove o argumento da lista
                img_proc.jsonoutput = False 
                args.remove('--nojson')                
        
        if args:                                # Se houver argumentos, processa-os como caminhos de imagem ou diretório  
            img_paths = []
            img_proc.its_console = True         # Identifica que a entrada é via console se houver argumentos

            for arg in args:                    
                if os.path.isdir(arg):                                                              # Se for um diretório, adiciona todas as imagens válidas dentro dele
                    extensions = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tif", "*.tiff", "*.webp") # Extensões de imagem suportados
                    for ext in extensions:                                                          # Itera sobre as extensões e adiciona as imagens ao img_paths
                        img_paths.extend(glob.glob(os.path.join(arg, ext)))                         # Adiciona todas as imagens ao img_paths
                else:                           # Se for um arquivo, adiciona diretamente
                    img_paths.append(arg)       # Adiciona o arquivo ao img_paths   
        else:                                   # Se não houver argumentos, abre o EasyGUI para seleção de imagens                    
            img_paths = easygui.fileopenbox(default=f"{load_path}/*",multiple=True, title="Selecione uma ou mais imagens para processar")
    except Exception as e:                                     # Em caso de erro na seleção da imagem
        print(f"Erro encontrado: {e}")
        print("Erro ao selecionar a imagem.")
        exit()                                  
    if not img_paths:                           # Se nenhuma imagem for encontrada ou selecionada 
        print("Nenhuma imagem selecionada.")    
        exit()                                  
    img_proc.load_image(img_paths)              # Após a imagem ser selecionada, chama a função load_image para o processamento
    
# === Execução do script principal ===
if __name__ == "__main__":                      # metodo main para execução direta do script PaddleGUI.py, devido o multiprocessing necessitar deste método 
    main()                                      