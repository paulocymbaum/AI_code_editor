#!/bin/bash
# Script to install dependencies and run the dashboard

set -e  # Exit on error

echo "🚀 Dashboard Setup and Run Script"
echo "================================"

# Check if demo directory exists
if [ ! -d "demo" ]; then
    echo "❌ Error: demo directory not found!"
    echo "Please run the dashboard creation script first:"
    echo "  python3 examples/create_dashboard_with_agent.py"
    exit 1
fi

cd demo

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in demo directory!"
    echo "The dashboard may not have been fully generated."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🚀 Starting development server..."
    echo "Dashboard will be available at: http://localhost:3000"
    echo ""
    npm run dev
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
