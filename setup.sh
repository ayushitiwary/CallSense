#!/bin/bash

# CallSense Setup Script for macOS/Linux

echo "=========================================="
echo "CallSense Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found"
echo ""

# Create virtual environment (optional but recommended)
echo "Would you like to create a virtual environment? (recommended) [y/N]"
read -r create_venv

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
    echo "To activate it, run: source venv/bin/activate"
    echo ""
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Setup .env file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OpenAI API key"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key to .env file"
echo "2. Run: python test_system.py (to verify setup)"
echo "3. Run: streamlit run app.py (to start the UI)"
echo ""
echo "For a quick demo: python quick_start.py"
echo ""

