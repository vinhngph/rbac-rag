# Backend Setup Instruction

## Prerequisites

- Python 3.13.x
- [Podman](https://podman.io/) (Recommended) OR [Docker](https://www.docker.com/)
- NVIDIA CUDA 13.x
- NVIDIA Container Toolkit

## Python Environment

Create and activate a virtual environment. This keeps the project's Python packages isolated from your system's global Python installation, preventing version conflicts.

```bash
python3 -m venv .venv
source ./.venv/bin/activate
```

## Python Dependencies

Install all required Python libraries and frameworks needed for the backend application to run properly.

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy the template environment file to create your own **.env** file. You can open this **.env** file later to configure your local secrets, database passwords,...

```bash
cp .env.template .env
```

## Container Network

Create an isolated virtual network. This allows your backend containers (PostgreSQL, Qdrant, Ollama) to securely discover and communicate with each other using their container names.

```bash
podman network create rbac_rag
```

## PostgreSQL

First, pull the PostgreSQL image. Then, run it as a detached container. This acts as the primary relational database for your application. The -v flag creates a volume to ensure your data is saved even if the container stops.

```bash
podman pull dhi.io/postgres:18-alpine3.23
```

```bash
podman run --name postgresql -d \
    --env-file .env \
    --network rbac_rag \
    -v postgresql-data:/var/lib/postgresql \
    dhi.io/postgres:18-alpine3.23
```

## Create database tables

Run the Alembic database migrations. This command connects to your running PostgreSQL instance and creates all the necessary tables and schemas required by the application.

```bash
alembic upgrade head
```

## Qdrant

Pull and run Qdrant, which serves as our vector database. This is essential for Retrieval-Augmented Generation (RAG) to store and quickly search through vector embeddings.

```bash
podman pull docker.io/qdrant/qdrant
```

```bash
podman run --name qdrant -d \
    -p 6333:6333 -p 6334:6334 \
    --network rbac_rag \
    -v qdrant-data:/qdrant/storage \
    qdrant/qdrant
```

## Ollama

Pull and run Ollama to host large language models locally. Notice the **--device nvidia.com/gpu=all** flag, which passes your physical NVIDIA GPU into the container to accelerate inference speeds.

```bash
podman pull docker.io/ollama/ollama
```

```bash
podman run --name ollama -d \
    -p 11434:11434 \
    --network rbac_rag \
    -v ollama-data:/root/.ollama \
    --device nvidia.com/gpu=all \
    ollama/ollama
```

## LLM Model

Execute a command inside the running Ollama container to download and run the specific Large Language Model (**gemma4:e2b-it-q4_K_M**) required for this project.

```bash
podman exec -it ollama ollama run gemma4:e2b-it-q4_K_M
```

## Run the server

Finally, start the FastAPI development server. This will launch the backend API, enabling hot-reloading so that any changes you make to the code are updated instantly.

```bash
fastapi dev
```
