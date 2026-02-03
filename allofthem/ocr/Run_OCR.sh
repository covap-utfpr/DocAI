#!/usr/bin/env bash

# ==========================================================
# run_ocr.sh
#
# Orquestra PaddleOCR, EasyOCR e Ollama Gladiator
# em ambientes isolados (venv + pyenv).
#
# Uso:
#   ./run_ocr.sh <imagem|diretório> [outros...]
# ==========================================================

####################################
# Configurações
####################################
PADDLE_VENV="PaddleOCR/bin/activate"
OLLAMA_VENV="Ollama_Gladiator/bin/activate"
EASYOCR_ENV="easyocr39"
OLLAMA_URL="http://localhost:11434"

set -e  # aborta o programa em caso de erro

####################################
# pyenv
####################################
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

####################################
# Validação de entrada
####################################
if [ "$#" -lt 1 ]; then
    echo "Uso: $0 <imagem|diretório> [outros arquivos...]"
    exit 1
fi

####################################
# Função: verifica se o Ollama Server está ativo
####################################
check_ollama() {
    if curl -s "${OLLAMA_URL}/api/tags" >/dev/null; then
        echo "🟣 Ollama está ativo"
        return 0
    else
        echo "❌ Ollama não está rodando (${OLLAMA_URL})"
        return 1
    fi
}

####################################
# Verificação antecipada do Ollama
####################################
echo "🔍 Verificando Ollama Server..."

if ! check_ollama; then
    echo "⛔ Pipeline abortado: Ollama é requisito obrigatório."
    exit 1
fi

echo
echo "🚀 Iniciando pipeline OCR..."
echo "📥 Entradas: $@"
echo

####################################
# PaddleOCR
####################################
echo "🔵 Executando PaddleOCR"
source "${PADDLE_VENV}"

python3 PaddleOCR/PaddleGUI.py "$@"

deactivate
echo "✅ PaddleOCR finalizado"
echo

####################################
# EasyOCR (pyenv)
####################################
echo "🟢 Executando EasyOCR"
pyenv activate "${EASYOCR_ENV}"

python EasyOCR/EasyOCR.py "$@"

pyenv deactivate
echo "✅ EasyOCR finalizado"
echo

####################################
# Ollama Gladiator
####################################
echo "🟣 Executando Ollama Gladiator"
source "${OLLAMA_VENV}"

python3 ollama_extract.py "$@"

deactivate
echo "✅ Ollama Gladiator finalizado"