#!/bin/bash
# Quick setup script for Professor Brusseau Digital Twin

set -e

echo "======================================"
echo "Professor Brusseau Digital Twin Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Create .env file:"
echo "   cp .env.example .env"
echo ""
echo "2. Edit .env and add your API keys"
echo ""
echo "3. Add course materials to:"
echo "   - data/raw/ai_ethics/"
echo "   - data/raw/business_ethics/"
echo ""
echo "4. Run data ingestion:"
echo "   python scripts/ingest_data.py"
echo ""
echo "5. Launch the application:"
echo "   python ui/gradio_app.py"
echo ""
echo "For detailed instructions, see GETTING_STARTED.md"
echo ""
