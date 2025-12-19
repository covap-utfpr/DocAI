from spellchecker import SpellChecker
from autocorrect import Speller
import re
from collections import Counter

# Dicionário personalizado com mapeamento de palavras específicas (separadas)
CUSTOM_DICTIONARY = {
    'codigo' : 'codigo',
    'qtde': 'quantidade',
    'un': 'unidade',
    'vlr.unit': 'valor unitario',
    'vlr.total': 'valor total',
    'para': 'para',
    'oramere': 'o numero',
    'grupoda': 'grupo da',
    'econamia': 'economia',
    'josta': 'vitor',
    'chapada': 'chapada',
    'cowercin': 'comércio',
    'de': 'de',
    'alinentos': 'alimentos',
    'ltda': 'ltda',
    'dr.lelino': 'dr laudelino',
    'dr': 'dr',
    'lelino': 'laudelino',
    'nncves': 'gonçalves',
    'chad': 'chapada',
    'pona': 'ponta',
    'nncves.332.chad.pona': 'gonçalves 332 chapada ponta',
    'grossa': 'grossa',
    'pr': 'pr',
    'grossa.pr': 'grossa pr',
    'fon': 'fone',
    'fon42)3239-0100': 'fone (42) 3239-0100',
    'docunento': 'documento',
    'auxiliar.da': 'auxiliar da',
    'nota': 'nota',
    'fiscal': 'fiscal',
    'cansumidor': 'consumidor',
    'eletronica': 'eletronica',
    'descrican': 'descricao',
    'file': 'file',
    'coxas': 'coxas',
    'filezinho': 'filezinho',
    'seara': 'seara',
    '1kg': '1kg',
    'aipim': 'aipim',
    'descas': 'descascado',
    'cong': 'congelado',
    'ti': 'ti',
    'carne': 'carne',
    'moida': 'moida',
    'bife': 'bife',
    'coxau': 'coxao',
    'mole': 'mole',
    'kg': 'kg',
    'bisc': 'biscoito',
    'renata': 'renata',
    'maiz360g': 'maizena 360g',
    '8isc': 'biscoito',
    'bate': 'bate',
    'rosca': 'rosca',
    '200g': '200g',
    'bolinha': 'bolinha',
    'gusnan': 'gusman',
    'padmultigrade': 'pao multigraos',
    'love': 'leve',
    'gusman': 'gusman',
    'panetone': 'panetone',
    'frutas': 'frutas',
    '500g': '500g',
    'bisnaguinha': 'bisnaguinha',
    'nino': 'nino',
    'int': 'integral',
    'pussata': 'passata',
    'tomate': 'tomate',
    'δ0s': '60g',
    'pussatn': 'passata',
    'tonate': 'tomate',
    'crene': 'creme',
    'kodtlar': 'kodilar',
    '6ög': '60g'
}

# Inicialização dos corretores para a linguagem PT-BR
spell_checker = SpellChecker(language='pt')
autocorrect_speller = Speller(lang='pt')

def check_custom_dictionary(word):        
    word_lower = word.lower().strip()           # Verifica se uma palavra individual está no dicionário personalizado.
    return CUSTOM_DICTIONARY.get(word_lower)    # Retorna a correção mapeada ou None se não encontrar.    

def spell_test(word, original_score):
    # Processa uma palavra através dos corretores ortográficos.    
    # Se for numérico, muito curto ou pontuação, retorna original
    if word.isnumeric() or len(word) <= 1 or word in ['.', ',', '!', '?', ':', ';', '-']: # Mantém números, pontuação e palavras muito curtas inalterados
        return word, original_score # Retorna a palavra original com a score original
    
    # 1. Verificar no dicionário personalizado primeiro, se encontrar retorna imediatamente com alta confiança
    custom_result = check_custom_dictionary(word)
    if custom_result:
        return custom_result, 100 # Retorna a correção do dicionário personalizado com alta confiança
    
    # 2. Verificar no SpellChecker, (mais basico)
    spell_checker_result = spell_checker.correction(word)
    if spell_checker_result is None:
        spell_checker_result = word # Se não houver sugestão, mantém a palavra original
    
    # 3. Verificar no Autocorrect (mais avançado)
    autocorrect_result = autocorrect_speller(word)
    
    # 4. Verificar no LanguageTool (mais complexo, mas pode falhar)
    #try:
    #    matches = language_tool.check(word)
    #    language_tool_result = word
    #    if matches:
    #        for match in matches:
    #            if match.replacements:
    #                language_tool_result = match.replacements[0]
    #                break
    #except:
    #    language_tool_result = word
    
    # Coletar todos os resultados e determinar um consenso entre os corretores
    results = [
        spell_checker_result,
        autocorrect_result, 
    #    language_tool_result
    ]
    
    # Filtrar resultados válidos
    valid_results = [result for result in results if result is not None and isinstance(result, str)]
    
    if not valid_results: 
        return word, original_score # Se nenhum corretor sugeriu algo, retorna original com confiança original baseada no OCR
    
    # Contar frequência dos resultados
    result_counts = Counter(valid_results)
    most_common = result_counts.most_common(1)

    # Se houver consenso entre os corretores, aplica a correção mas mantém o score original do OCR
    if most_common[0][1] >= 2 or (spell_checker_result != word and spell_checker_result != most_common[0][0]):
        return most_common[0][0], original_score  # Corrige mas mantém score OCR
    
    return word, original_score  # Mantém tudo original


# === função responsavel por corrigir as palavras do OCR via corretores ortograficos ===
def to_spellchecker(text, original_score):  # Processa texto do OCR através do corretor ortográfico com base na confiança original do OCR.
        
    if not text.strip():                # Se o texto estiver vazio, retorna vazio com score original
        return text, original_score
    
    if text.strip().isnumeric():        # Se o texto for apenas numérico, retorna original com a confiança do OCR  
        return text, original_score
    
    # Usar regex para separar palavras mantendo pontuação e espaços
    # Este padrão captura palavras (incluindo números e caracteres especiais) e pontuação individualmente
    tokens = re.findall(r'\b\w+\b|[.,!?;:-]|\s+', text)
    
    corrected_tokens = []
    confidence_scores = []
    
    for token in tokens: # Itera sobre cada token (palavra, pontuação ou espaço)
        if token.isspace() or token in ['.', ',', '!', '?', ':', ';', '-']:            
            corrected_tokens.append(token) # Mantém espaços e pontuação inalterados
            confidence_scores.append(100)  # Alta confiança para pontuação e espaços
        else:
            # Processa palavras através do corretor
            corrected_word, confidence  = spell_test(token, original_score) # Corrige a palavra e obtém a confiança
            corrected_tokens.append(corrected_word)                         # Adciona a palavra corrigida 
            confidence_scores.append(confidence)                            # Adiciona a confiança associada do corretor
    
    # Reconstruir o texto mantendo a estrutura original
    result = ''.join(corrected_tokens)
    
    # Calcular pontuação média (ignorando pontuação e espaços)
    word_scores = [score for i, score in enumerate(confidence_scores) 
                  if not (tokens[i].isspace() or tokens[i] in ['.', ',', '!', '?', ':', ';', '-'])]
    
    avg_confidence = sum(word_scores) / len(word_scores) if word_scores else original_score # Evita a divisão por zero, se não houver palavras retorna o score original
    
    return result, avg_confidence # Retorna o texto corrigido e a confiança média do corretor