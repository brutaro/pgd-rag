# 2b_enviar_arquivo_especifico_pinecone.py
from pinecone import Pinecone
import json
import sys
import config

# --- CONFIGURAÇÃO ---
NAMESPACE = "manual-participante"  # Mesmo namespace do script original

def enviar_arquivo_para_pinecone(caminho_arquivo):
    """
    Envia um arquivo JSON específico para o Pinecone.
    """
    print(f"Enviando arquivo: {caminho_arquivo}")
    print(f"Namespace: {NAMESPACE}")
    print()

    # --- Carregar arquivo JSON ---
    print(f"Carregando arquivo JSON...")
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        todos_documentos = json.load(f)
            
    print(f"Total de {len(todos_documentos)} documentos carregados.")

    # --- Conexão com o Pinecone ---
    print(f"Conectando ao Pinecone e ao índice '{config.PINECONE_INDEX_NAME}'...")
    try:
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        
        if config.PINECONE_INDEX_NAME not in pc.list_indexes().names():
            print(f"ERRO: O índice '{config.PINECONE_INDEX_NAME}' não existe.")
            return
            
        index = pc.Index(config.PINECONE_INDEX_NAME)
        print("-> Conexão estabelecida.")
    except Exception as e:
        print(f"ERRO ao conectar com Pinecone: {e}")
        return

    # --- Upsert dos Registros em Lotes ---
    print("Enviando registros para o Pinecone...")
    batch_size = 96
    
    try:
        for i in range(0, len(todos_documentos), batch_size):
            batch = todos_documentos[i:i + batch_size]
            print(f"Enviando batch de {len(batch)} documentos...")
            
            index.upsert_records(records=batch, namespace=NAMESPACE)

    except Exception as e:
        print(f"\n--- ERRO AO ENVIAR O BATCH ---")
        print(f"A operação de upsert falhou: {e}")
        return

    print(f"\n-> {len(todos_documentos)} documentos enviados com sucesso para o namespace '{NAMESPACE}'.")
    print("Envio concluído com sucesso!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python 2b_enviar_arquivo_especifico_pinecone.py <caminho_arquivo.json>")
        print("Exemplo: python 2b_enviar_arquivo_especifico_pinecone.py json_processados/manual-chefe-unidade-TELAS-DETALHADAS.json")
        sys.exit(1)
    
    enviar_arquivo_para_pinecone(sys.argv[1])
