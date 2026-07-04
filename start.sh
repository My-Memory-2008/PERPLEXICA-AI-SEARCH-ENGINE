#!/bin/bash

# 1. Update system and install Ollama
curl -fsSL https://ollama.com | sh

# 2. Start Ollama in the background
ollama serve > ollama.log 2>&1 &
echo "Waiting for Ollama to initialize..."
sleep 8

# 3. Pull required models and build the unfiltered version
ollama pull nomic-embed-text
ollama pull qwen2.5:1.5b
ollama create unrestricted-qwen -f ./Modelfile

# 4. Clone Perplexica core framework inside the space
git clone https://github.com framework
cp config.toml framework/config.toml

# 5. Move into framework directory and launch via Docker
cd framework
docker compose up -d
echo "Search Engine is completely launched!"
