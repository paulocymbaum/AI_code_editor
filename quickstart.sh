#!/bin/bash

# AI Coding Agent - Quick Start Script
# This script helps you get started quickly

set -e

echo "=================================="
echo "AI Coding Agent - Quick Start"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "Error: Python 3.11+ required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your GROQ_API_KEY"
    echo ""
    read -p "Do you have a Groq API key? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Groq API key: " groq_key
        if [[ -n "$groq_key" ]]; then
            sed -i.bak "s/your_groq_api_key_here/$groq_key/" .env
            rm .env.bak
            echo "API key saved to .env"
        fi
    else
        echo ""
        echo "Get your API key from: https://console.groq.com"
        echo "Then edit .env and add it manually"
    fi
else
    echo ".env file already exists"
fi

# Check if Docker is available
echo ""
echo "Checking Docker availability..."
if command -v docker &> /dev/null; then
    echo "Docker found"
    echo ""
    read -p "Do you want to start services with Docker? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting services with Docker Compose..."
        docker-compose up -d
        echo ""
        echo "Services started!"
        echo "- API Server: http://localhost:8000"
        echo "- API Docs: http://localhost:8000/docs"
        echo "- Prometheus: http://localhost:9090"
        echo "- Grafana: http://localhost:3000"
    fi
else
    echo "Docker not found (optional)"
fi

# Test the installation
echo ""
echo "Testing installation..."
python3 -c "
import sys
try:
    from groq import AsyncGroq
    from fastapi import FastAPI
    from pydantic import BaseModel
    print('✓ All core dependencies installed')
    sys.exit(0)
except ImportError as e:
    print(f'✗ Missing dependency: {e}')
    sys.exit(1)
"

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Make sure your GROQ_API_KEY is set in .env"
echo ""
echo "2. Run the example:"
echo "   python example_usage.py"
echo ""
echo "3. Start the API server:"
echo "   python api_server.py"
echo "   Then visit: http://localhost:8000/docs"
echo ""
echo "4. Or use Docker:"
echo "   docker-compose up"
echo ""
echo "5. Read the documentation:"
echo "   - README.md - Overview and features"
echo "   - SYSTEM_DESIGN.md - Architecture details"
echo "   - IMPLEMENTATION_GUIDE.md - Development guide"
echo ""
echo "For help, see: https://github.com/your-repo/issues"
echo ""
