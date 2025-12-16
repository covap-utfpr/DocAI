import base64, json, requests
import os, sys 
import Modules.path as path
import Modules.config as config
from Modules.json_processing import clear_data, to_json, save_json

# Modelos instalados via Ollama (pode ser instalado por meio do comando: ollama run <modelo>)
MODELOS_INSTALADOS = [
    "llama3.2-vision:11b",
    "gemma3:4b",
    "gemma3:12b",
    "ministral-3:3b",
    "ministral-3:8b",
    "ministral-3:14b",
    "qwen3-vl:2b",
    "qwen3-vl:4b",
    "qwen3-vl:8b",
]

# Converte a imagem para base64 para ser processado pelos modelos LLM, onde não é possível enviar o arquivo diretamente para os modelos
def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Função para extrair o texto da imagem usando o modelo do Ollama 
def extract_text_from_image(model_name, image_path):
    img_b64 = image_to_base64(image_path)

    prompt = """
Você é um modelo OCR.  
Sua única tarefa é analisar a imagem fornecida e retornar o texto detectado no formato estrito abaixo:

OCR='<texto_detectado>', score=<pontuação>, bbox=[x1,y1,x2,y2]

Regras:
- Não explique nada.
- Não adicione comentários.
- Não inclua nenhuma outra informação além das linhas OCR.
- Cada detecção deve estar em uma nova linha.
- Preserve vírgulas, pontos, acentos e símbolos exatamente como aparecem.
- Preserve o score com duas casas decimais quando possível.
- Preserve o formato do bbox exatamente como: [x1,y1,x2,y2].

Agora processe a imagem enviada e retorne APENAS as linhas OCR nesse formato.
"""

    payload = {
        "model": model_name,
        "prompt": prompt,
        "images": [img_b64]
    }

    # O modelo utiliza o Ollama pela API na porta 11434 para gerar todo o fluxo de OCR baseado no prompt
    response = requests.post("http://localhost:11434/api/generate", json=payload, stream=True)

    texto = ""

    # Utiliza o formato NDJSON para o processamento em streaming
    for line in response.iter_lines():
        if not line:
            continue
        try:
            obj = json.loads(line.decode("utf-8"))
            # concatena o texto parcial
            if "response" in obj:
                texto += obj["response"]
        except Exception as e:
            print("[ERRO DECODIFICAÇÃO NDJSON]", e)
            continue

    # retorna texto final dividido em linhas
    return texto.splitlines()

def save_ocr_results(lines, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def expand_input_paths(paths):
    # Recebe caminhos (arquivos ou diretórios) e retorna uma lista final apenas com arquivos de imagem válidos.    
    valid_ext = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

    arquivos = [] # Cria a lista dos arquivos a serem processados

    for p in paths:
        # Se for um arquivo adiciona diretamente
        if os.path.isfile(p):
            arquivos.append(p)

        # Se for um diretório percorre buscando arquivos de imagem
        elif os.path.isdir(p):            
            for root, dirs, files in os.walk(p):
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in valid_ext:
                        arquivos.append(os.path.join(root, f))
        # Se não encontrar o caminho, avisa
        else:
            print(f"[AVISO] Caminho ignorado (não existe): {p}")

    return arquivos  # Retorna a lista final de arquivos a serem processados pelos modelos

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 ollama_extract.py <imagem1> ou <diretório> [...]")
        sys.exit(1)

    imagens = expand_input_paths(sys.argv[1:]) # Realiza o processamento das entradas

    results_dir = path.results # Diretório onde vai ficar salvo os resultados 

    for image_file in imagens: # Para cada imagem:

        if not os.path.exists(image_file):
            print(f"[ERRO] Arquivo não encontrado: {image_file}")
            continue
    
        base_name = os.path.basename(image_file)
        base_no_ext = os.path.splitext(base_name)[0]
    
        for model_name in MODELOS_INSTALADOS:
            print(f"Processando {image_file} com {model_name}...")
    
            try:                
                # OCR                
                ocr_lines = extract_text_from_image(model_name, image_file) # Processa baseado no modelo e string fornecida
    
                ocr_txt_path = os.path.join(
                    results_dir,
                    f"{base_no_ext}_{model_name}_ocr.txt"
                )
    
                save_ocr_results(ocr_lines, ocr_txt_path)   # Salva o resultado do OCR no formato .txt
                print(f"OCR salvo em: {ocr_txt_path}")
                    
                # TXT → TOKENS                
                tokens = config.parse_ocr_txt(ocr_txt_path) # Faz um parse para processar o arquivo em formato json posteriormente
    
                if not tokens:
                    print("[AVISO] Nenhum token válido encontrado.")
                    continue
                    
                # TOKENS → JSON                
                clear_data() # Limpa dados anteriores antes de salvar um novo json
    
                palavras = [t["text"] for t in tokens] # Extrai apenas o texto dos tokens
                to_json(palavras) # Converte para o formato json
    
                json_path = save_json(
                    filename=f"{base_no_ext}_{model_name}",
                    output_dir=results_dir
                )
    
            except Exception as e:
                print(f"[ERRO] Falha com {model_name}: {e}")    