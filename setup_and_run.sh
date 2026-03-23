#!/usr/bin/env bash
# setup_and_run.sh - One-command setup and launch for the Tata Competitive Intel Dashboard

set -e

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🔭  Tata Communications — Competitive Intelligence Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✅ Python: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data..."
python3 -c "
import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('vader_lexicon', quiet=True)
print('  NLTK data ready.')
"

# Create data directory
mkdir -p data

# Pre-populate pricing data
echo "💾 Initializing pricing database..."
python3 -c "
from scrapers.pricing_tracker import load_pricing_data
d = load_pricing_data()
print(f'  Pricing DB ready — {sum(len(v) for k,v in d.items() if isinstance(v, dict))} products loaded.')
"

# Pre-populate product launches
echo "🚀 Initializing product launches data..."
python3 -c "
from data_manager import load_product_launches
launches = load_product_launches()
print(f'  Product launches ready — {len(launches)} entries loaded.')
"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅  Setup complete! Launching dashboard…"
echo "  🌐  Open http://localhost:8501 in your browser"
echo "  💡  Use the sidebar → 'Refresh All Data' to fetch live news"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Launch Streamlit
streamlit run app.py \
    --server.port 8501 \
    --server.headless false \
    --theme.base dark \
    --theme.primaryColor "#0033A0" \
    --theme.backgroundColor "#0A0F1E" \
    --theme.secondaryBackgroundColor "#111827" \
    --theme.textColor "#E8EDF5"
