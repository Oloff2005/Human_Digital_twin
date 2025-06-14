#!/bin/bash

echo "🔧 Setting up Human Digital Twin environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

mkdir -p data/raw data/processed data/external
echo "✅ Setup complete"
