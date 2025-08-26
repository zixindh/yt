#!/bin/bash

# Setup script for Qwen Coder CLI on Streamlit Cloud
echo "Setting up environment and Qwen Coder CLI..."

# Increase inotify limits to prevent file watching issues
echo "Setting inotify limits..."
if command -v sysctl &> /dev/null; then
    sysctl -w fs.inotify.max_user_watches=524288 2>/dev/null || echo "Could not set max_user_watches"
    sysctl -w fs.inotify.max_user_instances=512 2>/dev/null || echo "Could not set max_user_instances"
    sysctl -w fs.inotify.max_queued_events=16384 2>/dev/null || echo "Could not set max_queued_events"
    echo "Inotify limits set"
else
    echo "sysctl not available, skipping inotify setup"
fi

# Check if Node.js and npm are available
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

# Install Qwen Coder CLI globally using npm
echo "Installing @qwen-code/qwen-code globally..."
npm install -g @qwen-code/qwen-code

# Check installation location
echo "npm global prefix: $(npm config get prefix)"
echo "PATH: $PATH"

# Verify installation
if command -v qwen &> /dev/null; then
    echo "✅ Qwen Coder CLI found in PATH"
    echo "Qwen version info:"
    qwen --version
    echo "Qwen CLI location: $(which qwen)"
else
    echo "❌ Qwen Coder CLI not found in PATH"
    echo "Trying to find it manually..."
    find /usr -name "*qwen*" 2>/dev/null || echo "Not found in /usr"
    find /home -name "*qwen*" 2>/dev/null || echo "Not found in /home"

    # Try to run it directly
    if [ -f "$(npm config get prefix)/bin/qwen" ]; then
        echo "Found qwen at: $(npm config get prefix)/bin/qwen"
        export PATH="$(npm config get prefix)/bin:$PATH"
        echo "✅ Added to PATH"
    else
        echo "❌ Qwen Coder CLI installation failed"
        exit 1
    fi
fi

echo "Setup complete!"
