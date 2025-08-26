#!/bin/bash

# Install Node.js 20.x
apt-get update
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install Qwen Coder CLI globally
npm install -g @qwen-code/qwen-code

echo "Setup complete!"
