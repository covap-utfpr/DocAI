import re
import os
import json
from datetime import datetime
from validate_docbr import CPF, CNPJ

import Modules.path as path
# ----------------------
# Estrutura de dados
# ----------------------

class NotaFiscal:
    def __init__(self):
        self.chave_acesso = None
        self.cnpj_estabelecimento = None
        self.cpf = None
        self.data_emissao = None
        self.nome_estabelecimento = None
        self.total_itens = 0
        self.valor_total = 0.0
        self.valor_total_desconto = 0.0
        self.valor_total_pago = 0.0
        self.itens = []
        
    def to_dict(self):        
        data_str = None
        if self.data_emissao: # Formata a data com espaço em vez do T 
            data_str = self.data_emissao.strftime('%Y-%m-%d %H:%M:%S')

        return {
            "chave_acesso": self.chave_acesso,
            "cnpj_estabelecimento": self.cnpj_estabelecimento,
            "cpf": self.cpf,
            "data_emissao": data_str,
            "itens": [item.to_dict() for item in self.itens],
            "nome_estabelecimento": self.nome_estabelecimento,
            "total_itens": self.total_itens,
            "valor_total": round(self.valor_total, 2),
            "valor_total_desconto": round(self.valor_total_desconto, 2),
            "valor_total_pago": round(self.valor_total_pago, 2)
        }

# Classe para representar um item da nota fiscal
class ItemNotaFiscal:
    def __init__(self):
        self.codigo = None
        self.desconto = 0.0
        self.descricao = None
        self.numero = None
        self.preco_total = 0.0
        self.preco_unitario = 0.0
        self.quantidade = 0
        
    def to_dict(self):
        return {
            "codigo": self.codigo,
            "desconto": self.desconto,
            "descricao": self.descricao,
            "numero": self.numero,
            "preco_total": self.preco_total,
            "preco_unitario": self.preco_unitario,
            "quantidade": self.quantidade
        }

# ----------------------
# Validações básicas
# ----------------------

nota_fiscal = NotaFiscal() # Instância global para armazenar os dados da nota 
current_item = None        # Item atual a ser processado
next_description = False   # Flag para indicar se a próxima linha é descrição  
next_price = False         # Flag para indicar se a próxima linha é preço
next_weight = False        # Flag para indicar se a próxima linha é unidade/peso

def cpf_validation(cpf: str) -> bool:   # Validação CPR com biblioteca docbr
    cpf = re.sub(r'\D', '', cpf)        # Remove caracteres não numéricos
    if len(cpf) != 11:                  # CPF deve ter 11 digitos
        return False
    return CPF().validate(cpf)          # Usa a biblioteca para validar o CPF

def cnpj_validation(cnpj: str) -> bool: # Validação CNPJ com biblioteca docbr
    cnpj = re.sub(r'\D', '', cnpj)      # Remove caracteres não numéricos 
    if len(cnpj) != 14:                 # CNPJ deve ter 14 digitos
        return False
    return CNPJ().validate(cnpj)       # Usa a biblioteca para validar o CNPJ

# ----------------------
# Classificadores
# ----------------------

def is_cpf(text: str):                              # O item é um CPF?
    text = re.sub(r'\D', '', text)                  # Remove caracteres não numéricos
    text = text.strip()                             # Remove espaços em branco 
    if len(text) == 11 and cpf_validation(text):    # Verifica se tem 11 digitos e é valido 
        nota_fiscal.cpf = CPF().mask(text)          # Formata o CPF com máscara
        return True
    return False

def is_cnpj(text: str):                                         # O item é um CNPJ?     
    text = re.sub(r'\D', '', text)                              # Remove caracteres não numéricos  
    text = text.strip()                                         # Remove espaços em branco  
    if len(text) == 14 and cnpj_validation(text):               # Verifica se tem 14 digitos e é valido  
        nota_fiscal.cnpj_estabelecimento = CNPJ().mask(text)    # Formata o CPNJ com máscara
        return True
    return False

def is_establishment_name(text: str):  # O item é um estabelicimento baseado nas palavras chave?
    text_lower = text.lower()          # Converte para minúsculas para facilitar a verificação 
    if any(local in text_lower for local in ['padaria', 'mercado', 'supermercado', 'loja', 'restaurante', 'ltda', 'comercio']): # Palavras chaves
        nota_fiscal.nome_estabelecimento = text.strip() # Armazena o nome do estabelecimento 
        return True
    return False

def is_key_acess(text: str):          # O item é uma chave de acesso?
    text = re.sub(r'\D', '', text)    # Remove caracteres não numéricos
    text = text.strip()               # Remove espaços em branco 
    if len(text) == 44:               # Verifica se tem 44 digitos  
        nota_fiscal.chave_acesso = text
        return True
    return False

def is_phone(text: str):              # O item é um telefone?
    text = re.sub(r'\D', '', text)    # Remove caracteres não numéricos
    text = text.strip()               # Remove espaços em branco
    if 10 <= len(text) <= 11:         # Verifica se tem 10 ou 11 digitos (com DDD)
        return True
    return False

def is_date(text: str):               # O item é uma data?  
    try:
        text = text.strip()
        
        # Primeiro, tenta separar data e hora que podem estar coladas
        # Padrões comuns: DD-MM-AAHH:MM:SS, DD/MM/AAHH:MM:SS, etc.
        patterns = [
            r'(\d{2}[-/]\d{2}[-/]\d{2})(\d{2}:\d{2}:\d{2})',  # DD-MM-AAHH:MM:SS
            r'(\d{2}[-/]\d{2}[-/]\d{4})(\d{2}:\d{2}:\d{2})', # DD-MM-AAAAHH:MM:SS
            r'(\d{2}[-/]\d{2}[-/]\d{2})[T\s]?(\d{2}:\d{2}:\d{2})',  # Com separador T ou espaço
        ]
        
        for pattern in patterns:                # Tenta os padrões acima
            match = re.match(pattern, text)     # Se combinar
            if match:
                data_part = match.group(1)      # Extrai as partes da data e hora
                hora_part = match.group(2)
                text = f"{data_part} {hora_part}"
                break
        
        # Lista de formatos para tentar parsear
        formats = [
            '%d-%m-%y %H:%M:%S',    # 03-09-24 10:53:31
            '%d/%m/%y %H:%M:%S',    # 03/09/24 10:53:31
            '%d-%m-%Y %H:%M:%S',    # 03-09-2024 10:53:31
            '%d/%m/%Y %H:%M:%S',    # 03/09/2024 10:53:31
            '%d-%m-%y',             # Apenas data
            '%d/%m/%y',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%y-%m-%d %H:%M:%S',    # Formato ISO
            '%Y-%m-%d %H:%M:%S',
        ]
        
        for fmt in formats:                               # Tenta cada formato 
            try:
                date_obj = datetime.strptime(text, fmt)   # Tenta parsear a data
                nota_fiscal.data_emissao = date_obj       # Armazena a data na nota fiscal
                return True
            except ValueError:
                continue
                
    except Exception as e:
        print(f"Erro ao parsear data: {e}")
    
    return False

def is_product_code(text: str):                     # O item é um código de produto?
    global next_description, current_item           # Usa variáveis globais para controlar o estado
    text = text.strip()                             # Remove espaços em branco
    if re.fullmatch(r"\b\d{5,14}\b", text):         # Verifica se é um número entre 5 e 14 dígitos        
        if current_item and current_item.codigo:    # Finaliza o item anterior em processamento se existir 
            nota_fiscal.itens.append(current_item)  # Adiciona o item à lista de itens da nota fiscal
            nota_fiscal.total_itens += 1            # Incrementa o contador de itens
        
        current_item = ItemNotaFiscal()                      # Cria novo item
        current_item.codigo = text                           # Armazena o código do produto
        current_item.numero = len(nota_fiscal.itens) + 1     # Define o número do item (baseado na quantidade atual de itens processados)
        next_description = True                              # Próxima linha deve ser a descrição do produto
        return True
    return False

def is_description(text: str):                  # O item é uma descrição de produto?
    global next_description, current_item       # Usa variáveis globais para controlar o estado
    if next_description and current_item:       # Se a flag estiver setada e houver um item atual   
        current_item.descricao = text.strip()   # Armazena a descrição do produto
        next_description = False                # Reseta a flag   
        return True
    return False

def is_price(text: str):                        # O item é um preço?
    global next_price, current_item             # Usa variáveis globais para controlar o estado  
    text = text.strip().replace(",", ".")       # Remove espaços em branco e substitui vírgula por ponto
    if re.fullmatch(r"^\d+(\.\d{2})$", text):   # Verifica se é um número com 2 casas decimanis
        price_value = float(text)               # Converte para float
        
        if current_item:                                     # Se houver um item atual
            if current_item.preco_unitario == 0.0:           # Se o preço unitario não estiver definido
                current_item.preco_unitario = price_value    # Definir preço unitário
            else:                               
                current_item.preco_total = price_value       # Define o preço total                 
                if current_item.preco_unitario > 0:          # Calcula quantidade baseada nos preços
                    current_item.quantidade = round(current_item.preco_total / current_item.preco_unitario, 2) # Quantidade arredondada para 2 casas decimais
        
        # Atualiza totais da nota fiscal
        nota_fiscal.valor_total += price_value
        nota_fiscal.valor_total_pago += price_value
        
        return True
    return False

def is_weight_unit(text: str):  # O item é uma unidade de peso ou medida baseada em kg, g, l, ml, un?       
    global current_item         # Usa variável global para o item atual
    text = text.strip()         # Remove espaços em branco 
    if re.fullmatch(r"^\d*[.,]?\d*(kg|KG|Kg|un|UN|Un|g|G|l|L|ml|ML)$", text): # Verifica o padrão de peso/unidade
        if current_item:            
            weight_match = re.match(r"^(\d*[.,]?\d*)", text)           # Extrai o valor numérico do peso/unidade
            if weight_match:                                           # Se encontrou um valor
                weight_str = weight_match.group(1).replace(",", ".")   # Subtitui vírgula por ponto
                try:
                    current_item.quantidade = float(weight_str)        # Converte para float e armazena como quantidade  
                except ValueError:
                    pass
        return True
    return False

# ----------------------
# Processamento principal
# ----------------------

def process_text(text: str): # Processa um texto e classifica em uma das categorias    
    text = text.strip()
    if not text:
        return
    
    # Ordem de verificação importante!
    classifiers = [
        is_key_acess,
        is_cnpj,
        is_cpf,
        is_establishment_name,
        is_date,
        is_phone,
        is_product_code,
        is_description,
        is_price,
        is_weight_unit
    ]
    
    for classifier in classifiers:
        if classifier(text):
            return

def to_json(palavras):
    # Processa uma lista de palavras ou uma única palavra
    if isinstance(palavras, str):
        process_text(palavras)
    elif isinstance(palavras, list):
        for palavra in palavras:
            process_text(palavra)

def create_json():
    # Cria o JSON final com os dados processados    
    global current_item
    if current_item and current_item.codigo:                # Finaliza o último item se existir
        nota_fiscal.itens.append(current_item)              # Adiciona o item à lista de itens da nota fiscal 
        nota_fiscal.total_itens = len(nota_fiscal.itens)    # Atualiza o total de itens
        current_item = None                                 # Reseta o item atual 
        
    # 🔑 recalcula total com base nos itens
    nota_fiscal.total_itens = len(nota_fiscal.itens)
    nota_fiscal.valor_total = sum(item.preco_total for item in nota_fiscal.itens)                               # Soma os preços totais dos itens
    nota_fiscal.valor_total_pago = nota_fiscal.valor_total - sum(item.desconto for item in nota_fiscal.itens)   # Subtrai os descontos dos itens do valor total

    result = nota_fiscal.to_dict()                          # Converte para dicionário
    return json.dumps(result, ensure_ascii=False, indent=2) # Converte para JSON string

def save_json(filename=None, output_dir=path.results): 
    # Salva o JSON atual processado em um arquivo.
    
    try:    
        json_data = create_json()                                   # Obtém os dados JSON processados 
                
        if not os.path.exists(output_dir):                          # Cria o diretório se não existir
            os.makedirs(output_dir) 
                
        if filename is None:                                        # Gera nome do arquivo se não fornecido baseado na data/hora e CNPJ/CPF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
            if nota_fiscal.cnpj_estabelecimento:                   # Usa CNPJ ou CPF no nome do arquivo se disponível
                cnpj_clean = re.sub(r'\D', '', nota_fiscal.cnpj_estabelecimento)
                filename = f"nota_{cnpj_clean}_{timestamp}.json"
            elif nota_fiscal.cpf:
                cpf_clean = re.sub(r'\D', '', nota_fiscal.cpf)
                filename = f"nota_{cpf_clean}_{timestamp}.json"
            else:
                filename = f"nota_fiscal_{timestamp}.json"
                
        if not filename.endswith('.json'): # Garante a extensão .json
            filename += '.json'
                
        filepath = os.path.join(output_dir, filename) # Caminho completo do arquivo
                
        with open(filepath, 'w', encoding='utf-8') as file: # Salva o arquivo
            file.write(json_data)

        print(f"Json gravado local: file://{os.path.abspath(filepath)}")                                                     
        return filepath
        
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")
        return None

def clear_data():
    # Limpa os dados para processar uma nova nota
    global nota_fiscal, current_item, next_description, next_price, next_weight
    nota_fiscal = NotaFiscal()
    current_item = None
    next_description = False
    next_price = False
    next_weight = False