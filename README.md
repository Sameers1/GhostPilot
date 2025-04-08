# GhostPilot - AI Automation Assistant

## LLM Setup Instructions

### Prerequisites
- Docker and Docker Compose installed on your system
- At least 8GB of RAM (16GB recommended)
- 20GB of free disk space

### Setting up the LLM

1. Start the Ollama container:
```bash
docker-compose up -d
```

2. Pull a model (we recommend using LLaVA for image analysis):
```bash
docker exec ollama ollama pull llava
```

3. Verify the installation:
```bash
docker exec ollama ollama list
```

### Running the Application

1. Make sure the Ollama container is running:
```bash
docker ps
```

2. Start the GhostPilot application:
```bash
python main.py
```

3. Click "Start Screenshots" to begin capturing and analyzing screenshots.

### Troubleshooting

If you encounter any issues:

1. Check if the Ollama container is running:
```bash
docker ps
```

2. Check the container logs:
```bash
docker logs ollama
```

3. Restart the container if needed:
```bash
docker-compose restart
```

### Available Models

You can use any of these models with Ollama:
- llava (recommended for image analysis)
- mistral
- llama2
- codellama

To switch models, pull the new model and update the model name in the application code. 