#!/bin/bash

# Deployment script for Discord Bot on Ubuntu Server

echo "🚀 Starting Discord Bot Deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip if not installed
echo "🐍 Installing Python3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.example .env
    echo "❗ IMPORTANT: Edit .env file and add your Discord token and API keys!"
    echo "   Run: nano .env"
fi

echo "✅ Deployment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your tokens: nano .env"
echo "2. Start the bot: ./run.sh"
echo "3. (Optional) Setup as a service: sudo ./setup_service.sh"

