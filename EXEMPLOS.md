# Exemplos de Uso

Este documento contém exemplos práticos de como usar o sistema PGD RAG.

## 📋 Exemplos

### 1. Processar Manual com Telas de Sistema

```bash
# Processar manual do administrador (contém telas de sistema)
python processar_pdf_completo.py \
  documentos_para_processar/manual-administrador-negocial-pgd-petrvs.pdf \
  json_processados/manual-administrador-COMPLETO.json
```

**Saída Esperada:**
```
================================================================================
PROCESSAMENTO COMPLETO DE PDF
================================================================================

📄 PDF: manual-administrador-negocial-pgd-petrvs.pdf
📁 Saída: json_processados/manual-administrador-COMPLETO.json
🖼️  Processar telas: Sim

📊 Total de páginas: 7

Configurando Gemini Vision...
✅ Modelo: gemini-2.5-flash

Processando páginas...
--------------------------------------------------------------------------------

Processando: 100%|██████████| 7/7 [03:13<00:00, 27.60s/página]

================================================================================
PROCESSAMENTO CONCLUÍDO
================================================================================
✅ Total de documentos criados: 7

📊 DETECÇÃO HÍBRIDA:
   Páginas com tela detectadas (heurística): 5
   Páginas sem tela detectadas (heurística): 0
   Páginas ambíguas → confirmadas com Vision: 2
   Páginas ambíguas → rejeitadas (sem tela): 0

🔍 PROCESSAMENTO VISION:
   Visão processada: 7 sucessos, 0 erros

📝 Total de palavras: 4,943
📁 JSON salvo em: json_processados/manual-administrador-COMPLETO.json
================================================================================
```

---

### 2. Processar Documento Apenas Textual

```bash
# Processar portaria (apenas texto normativo)
python processar_pdf_completo.py \
  documentos_para_processar/portaria-dnit-5283-2024.pdf \
  json_processados/portaria-COMPLETO.json
```

**Saída Esperada:**
```
📊 DETECÇÃO HÍBRIDA:
   Páginas com tela detectadas (heurística): 3
   Páginas sem tela detectadas (heurística): 2
   Páginas ambíguas → confirmadas com Vision: 1
   Páginas ambíguas → rejeitadas (sem tela): 6

🔍 PROCESSAMENTO VISION:
   Visão processada: 4 sucessos, 0 erros
   📉 Economia: 7 página(s) sem chamadas Vision (58%)
```

---

### 3. Processar Sem Análise Visual

```bash
# Processar apenas texto (sem Vision)
python processar_pdf_completo.py \
  documentos_para_processar/portaria-dnit-5283-2024.pdf \
  json_processados/portaria-TEXTO.json \
  --sem-telas
```

**Vantagens:**
- ⚡ Mais rápido (sem chamadas de API)
- 💰 Sem custos de API
- ✅ Ideal para documentos apenas textuais

---

### 4. Enviar para Pinecone

```bash
# Enviar JSON gerado para Pinecone
python 2b_enviar_arquivo_especifico_pinecone.py \
  json_processados/manual-administrador-COMPLETO.json
```

**Saída Esperada:**
```
Enviando arquivo: json_processados/manual-administrador-COMPLETO.json
Namespace: manual-participante

Carregando arquivo JSON...
Total de 7 documentos carregados.

Conectando ao Pinecone e ao índice 'pgd-rag'...
-> Conexão estabelecida.

Enviando registros para o Pinecone...
Enviando batch de 7 documentos...

-> 7 documentos enviados com sucesso para o namespace 'manual-participante'.
Envio concluído com sucesso!
```

---

### 5. Pipeline Completo

```bash
# 1. Processar PDF
python processar_pdf_completo.py \
  documentos_para_processar/manual-informacoes-gerais-pgd-petrvs.pdf \
  json_processados/manual-informacoes-gerais-COMPLETO.json

# 2. Enviar para Pinecone
python 2b_enviar_arquivo_especifico_pinecone.py \
  json_processados/manual-informacoes-gerais-COMPLETO.json
```

---

## 🔍 Verificar JSON Gerado

```bash
# Ver estrutura do JSON gerado
python -c "
import json
with open('json_processados/manual-administrador-COMPLETO.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)
    
print(f'Total de chunks: {len(dados)}')
print(f'Total de palavras: {sum(d[\"num_palavras\"] for d in dados):,}')
print(f'Chunks com instruções: {sum(1 for d in dados if d.get(\"tem_instrucoes_navegacao\"))}')
print()
print('Primeiro chunk:')
print(f\"  ID: {dados[0]['id']}\")
print(f\"  Título: {dados[0]['task_title']}\")
print(f\"  Tipo: {dados[0]['chunk_type']}\")
print(f\"  Palavras: {dados[0]['num_palavras']}\")
"
```

---

## 📊 Análise de Resultados

```bash
# Analisar chunks gerados
python -c "
import json
with open('json_processados/manual-administrador-COMPLETO.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Estatísticas
chunks_com_instrucoes = sum(1 for d in dados if d.get('tem_instrucoes_navegacao'))
chunks_contexto = sum(1 for d in dados if d['chunk_type'] == 'contexto')
chunks_texto = sum(1 for d in dados if d['chunk_type'] == 'texto')

print('📊 Estatísticas:')
print(f'  Total de chunks: {len(dados)}')
print(f'  Com instruções: {chunks_com_instrucoes}')
print(f'  Tipo contexto: {chunks_contexto}')
print(f'  Tipo texto: {chunks_texto}')
print(f'  Total de palavras: {sum(d[\"num_palavras\"] for d in dados):,}')
"
```

---

## 🐛 Troubleshooting

### Erro: API Key não encontrada

```bash
# Verificar se .env existe e tem as chaves
cat .env
```

**Solução:** Certifique-se de que o arquivo `.env` existe e contém:
```env
GOOGLE_API_KEY=sua_chave_aqui
```

### Erro: PDF não encontrado

```bash
# Verificar se o arquivo existe
ls -lh documentos_para_processar/*.pdf
```

**Solução:** Verifique o caminho do arquivo PDF.

### Erro: Vision API rate limit

**Solução:** O script tem retry automático. Aguarde alguns minutos e tente novamente.

---

## 💡 Dicas

1. **Documentos grandes**: Use detecção híbrida (padrão) para economizar API
2. **Documentos apenas textuais**: Use `--sem-telas` para processamento rápido
3. **Testes**: Use PDFs pequenos primeiro para validar o fluxo
4. **Monitoramento**: Observe as métricas de detecção híbrida para otimizar

---

**Para mais informações, consulte o [README.md](README.md)**

