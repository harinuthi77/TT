#!/bin/bash

echo "🤖 Universal AI Agent - Setup Script"
echo "===================================="
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if (( $(echo "$python_version >= $required_version" | bc -l) )); then
    echo "   ✅ Python $python_version detected"
else
    echo "   ❌ Python 3.8+ required (found $python_version)"
    exit 1
fi

# Install dependencies
echo ""
echo "2️⃣  Installing Python packages..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "   ✅ Packages installed"
else
    echo "   ❌ Package installation failed"
    exit 1
fi

# Install Playwright browsers
echo ""
echo "3️⃣  Installing Playwright browsers..."
playwright install chromium
if [ $? -eq 0 ]; then
    echo "   ✅ Chromium installed"
else
    echo "   ❌ Browser installation failed"
    exit 1
fi

# Check API key
echo ""
echo "4️⃣  Checking API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "   ⚠️  ANTHROPIC_API_KEY not set"
    echo ""
    echo "   Please set it with:"
    echo "   export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
else
    echo "   ✅ API key is set"
fi

# Create directories
echo ""
echo "5️⃣  Creating directories..."
mkdir -p workspace results/screenshots
echo "   ✅ Directories created"

# Done
echo ""
echo "===================================="
echo "✅ Setup complete!"
echo ""
echo "Run the agent with:"
echo "   python main.py"
echo ""