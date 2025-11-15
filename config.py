# config.py
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações da API do Google
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")  # Alias para compatibilidade

# Configurações do Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD")
PINECONE_REGION = os.getenv("PINECONE_REGION")