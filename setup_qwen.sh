#!/bin/bash

# Setup script for Qwen Coder CLI on Streamlit Cloud
echo "Setting up Qwen Coder CLI..."

# Check Node.js version (should be 18+ from packages.txt)
echo "Node.js version: $(node --version)"
NODE_VERSION=$(node --version | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Warning: Node.js version $NODE_VERSION is less than required 18+"
    echo "The packages.txt should have installed Node.js 18"
fi

# Install Qwen Coder CLI using npm
echo "Installing @qwen-code/qwen-code..."
npm install -g @qwen-code/qwen-code

# Verify installation
if command -v qwen &> /dev/null; then
    echo "✅ Qwen Coder CLI installed successfully"
    echo "Location: $(which qwen)"
else
    echo "❌ Qwen Coder CLI installation failed"
    echo "Trying npx approach instead..."
fi

echo "Setup complete!"
