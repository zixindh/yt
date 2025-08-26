#!/bin/bash

# Setup script for Qwen Coder CLI on Streamlit Cloud
echo "Setting up Qwen Coder CLI..."

# Install Qwen Coder CLI globally using npm
npm install -g @qwen-code/qwen-code

# Verify installation
if command -v qwen &> /dev/null; then
    echo "✅ Qwen Coder CLI installed successfully"
    qwen --version
else
    echo "❌ Qwen Coder CLI installation failed"
    exit 1
fi

echo "Setup complete!"
