#!/bin/bash

echo "🔧 Setting up Human Digital Twin environment..."

# Export variables from .env if it exists and the script is sourced
if [ -f ".env" ]; then
  # enable automatic export of all variables
  set -o allexport
  source .env
  set +o allexport
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pandas numpy matplotlib streamlit openai
pip freeze > requirements.txt
mkdir -p data/raw data/processed data/external

echo "✅ Setup complete"
