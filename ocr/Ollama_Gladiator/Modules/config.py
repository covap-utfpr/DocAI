import re

def parse_ocr_txt(txt_file):
    """
    Lê o txt salvo pelo OCR e retorna uma lista de dicionários:
    [
      {"text": "ARROZ", "score": 0.95},
      ...
    ]
    """
    pattern = r"OCR='(.*?)', score=([\d.]+)"
    tokens = []

    with open(txt_file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                tokens.append({
                    "text": match.group(1).strip(),
                    "score": float(match.group(2))
                })

    return tokens
