#!/bin/bash

echo "=========================================="
echo "ICMS Backend Setup Script"
echo "=========================================="

# Navigate to Backend directory
cd Backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your-secret-key-change-in-production-use-openssl-rand-hex-32/$SECRET_KEY/" .env
    
    echo "✓ .env file created with generated SECRET_KEY"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs uploads

echo ""
echo "=========================================="
echo "✓ Backend setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review and update Backend/.env if needed"
echo "  2. Run seed script: python3 scripts/seed_data.py"
echo "  3. Start server: cd Backend && source venv/bin/activate && uvicorn core.main:app --reload"
echo ""
