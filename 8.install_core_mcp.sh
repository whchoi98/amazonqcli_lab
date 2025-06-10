#!/bin/bash

# Installation script for Python 3.12, uv, and Node.js on Amazon Linux 2023

echo "===== INSTALLATION STARTED ====="
echo "Installing Python 3.12, uv package manager, and Node.js"

# Install development tools and libraries
echo "===== Installing development tools and libraries ====="
sudo dnf groupinstall "Development Tools" -y
sudo dnf install openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel -y

# Install Python 3.12
echo "===== Installing Python 3.12 ====="
cd /tmp
wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
tar xzf Python-3.12.0.tgz
cd Python-3.12.0
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall

# Check Python version
echo "===== Python 3.12 installation completed ====="
python3.12 --version

# Install uv
echo "===== Installing uv package manager ====="
curl -LsSf https://astral.sh/uv/install.sh | sh

# Check uv version
echo "===== uv installation completed ====="
uv --version

# Install Node.js (user selection)
echo "Select Node.js installation method:"
echo "1) Install from default repository"
echo "2) Install Node.js 20.x from NodeSource"
echo "3) Install via nvm"
read -p "Select option (1-3): " node_option

case $node_option in
  1)
    echo "===== Installing Node.js from default repository ====="
    sudo dnf install -y nodejs
    ;;
  2)
    echo "===== Installing Node.js 20.x from NodeSource ====="
    curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
    sudo dnf install -y nodejs
    ;;
  3)
    echo "===== Installing Node.js via nvm ====="
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
    echo "nvm installation completed. Reloading shell."
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    nvm install --lts
    ;;
  *)
    echo "Invalid selection. Skipping Node.js installation."
    ;;
esac

# Verify installation
echo "===== Installation completed ====="
echo "Python version:"
python3.12 --version
echo "uv version:"
uv --version
echo "Node.js version:"
node --version
echo "npm version:"
npm --version

echo "===== All installations completed successfully ====="