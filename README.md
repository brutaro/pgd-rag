# PGD RAG - Sistema de Processamento de PDFs para RAG

Sistema completo para processamento de documentos PDFs do Programa de Gestão e Desempenho (PGD) Petrvs, com extração de texto, análise visual de telas de sistema usando Gemini Vision, e preparação para ingestão em banco de dados vetorial (Pinecone).

## 📋 Índice

- [Características](#características)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Fluxo de Processamento](#fluxo-de-processamento)
- [Detecção Híbrida de Telas](#detecção-híbrida-de-telas)
- [Exemplos](#exemplos)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## 🚀 Características

- ✅ **Extração de texto completa** usando PyMuPDF
- ✅ **Análise visual inteligente** de telas de sistema com Gemini Vision
- ✅ **Detecção híbrida de telas** (heurística + Vision) para economia de API
- ✅ **Instruções passo a passo** usando nomes exatos dos elementos do sistema
- ✅ **Processamento em lotes** com barras de progresso
- ✅ **Retry automático** em caso de falhas de API
- ✅ **JSON estruturado** pronto para ingestão no Pinecone
- ✅ **Suporte a documentos híbridos** (texto + telas)

---

## 🛠 Tecnologias

- **Python 3.10+**
- **PyMuPDF (fitz)** - Processamento de PDFs
- **Google Gemini Vision API** - Análise visual de telas
- **Pillow (PIL)** - Processamento de imagens
- **Pinecone** - Banco de dados vetorial
- **python-dotenv** - Gerenciamento de variáveis de ambiente
- **tqdm** - Barras de progresso

---

## 🏗 Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    PDF Input                                 │
│              (documentos_para_processar/)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           processar_pdf_completo.py                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Extração de Texto (PyMuPDF)                        │ │
│  │  2. Conversão para Imagem (Pixmap)                     │ │
│  │  3. Detecção Híbrida de Telas                          │ │
│  │     ├─ Heurística Local (sem API)                      │ │
│  │     ├─ Vision Flash (confirmação ambígua)              │ │
│  │     └─ Vision Pro (análise completa)                   │ │
│  │  4. Montagem de JSON com Metadados                     │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              JSON Estruturado                                │
│              (json_processados/)                             │
│  • Texto extraído                                            │
│  • Instruções de navegação                                   │
│  • Elementos da tela                                         │
│  • Campos de formulário                                      │
│  • Metadados completos                                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│       2b_enviar_arquivo_especifico_pinecone.py              │
│  • Envio para Pinecone                                       │
│  • Namespace configurável                                    │
│  • Processamento em lotes                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/pgd-rag.git
cd pgd-rag
```

2. **Crie um ambiente virtual:**
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

### 1. Variáveis de Ambiente

**⚠️ IMPORTANTE: NUNCA commite o arquivo `.env` com chaves reais!**

Crie um arquivo `.env` na raiz do projeto baseado no arquivo `env.example`:

```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar .env com suas chaves reais
nano .env  # ou use seu editor preferido
```

Conteúdo do `.env`:

```env
# Google Gemini API
# Obtenha sua chave em: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=sua_chave_api_gemini_aqui

# Pinecone (opcional - apenas se for enviar para Pinecone)
# Obtenha sua chave em: https://app.pinecone.io/
PINECONE_API_KEY=sua_chave_pinecone_aqui
PINECONE_INDEX_NAME=nome_do_indice
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

**🔒 Segurança:** O arquivo `.env` está no `.gitignore` e **NUNCA** será commitado.

### 2. Estrutura de Diretórios

O projeto espera a seguinte estrutura:

```
pgd-rag/
├── documentos_para_processar/    # PDFs a serem processados
├── json_processados/              # JSONs gerados (criado automaticamente)
├── config.py                      # Configurações
├── processar_pdf_completo.py      # Script principal
├── 2b_enviar_arquivo_especifico_pinecone.py  # Script Pinecone
├── requirements.txt               # Dependências
└── .env                           # Variáveis de ambiente (não commitado)
```

---

## 📖 Uso

### Processamento Básico

```bash
python processar_pdf_completo.py <caminho_pdf> <output_json>
```

**Exemplo:**
```bash
python processar_pdf_completo.py \
  documentos_para_processar/manual-administrador-negocial-pgd-petrvs.pdf \
  json_processados/manual-administrador-COMPLETO.json
```

### Processamento Sem Análise Visual (Apenas Texto)

```bash
python processar_pdf_completo.py <caminho_pdf> <output_json> --sem-telas
```

**Exemplo:**
```bash
python processar_pdf_completo.py \
  documentos_para_processar/portaria-dnit-5283-2024.pdf \
  json_processados/portaria-COMPLETO.json \
  --sem-telas
```

### Envio para Pinecone

```bash
python 2b_enviar_arquivo_especifico_pinecone.py <caminho_json>
```

**Exemplo:**
```bash
python 2b_enviar_arquivo_especifico_pinecone.py \
  json_processados/manual-administrador-COMPLETO.json
```

---

## 📁 Estrutura do Projeto

```
pgd-rag/
├── documentos_para_processar/          # PDFs originais
│   ├── manual-*.pdf
│   ├── portaria-*.pdf
│   └── ...
│
├── json_processados/                   # JSONs gerados (auto-criado)
│   └── *.json
│
├── config.py                           # Configurações e variáveis de ambiente
├── processar_pdf_completo.py           # Script principal de processamento
├── 2b_enviar_arquivo_especifico_pinecone.py  # Script de envio para Pinecone
├── requirements.txt                    # Dependências Python
├── README.md                           # Esta documentação
└── .env                                # Variáveis de ambiente (não commitado)
```

---

## 🔄 Fluxo de Processamento

### 1. Extração de Texto

O script extrai todo o texto do PDF usando PyMuPDF:

```python
texto_pagina = pagina.get_text("text").strip()
```

### 2. Conversão para Imagem

Cada página é convertida em imagem (pixmap) para análise visual:

```python
pixmap = pagina.get_pixmap(dpi=150)
```

### 3. Detecção Híbrida de Telas

O sistema usa três níveis de detecção:

#### Nível 1: Heurística Local (Rápida, Sem API)
- Analisa marcadores de tela no texto ("clicar em", "botão", "menu")
- Verifica instruções passo a passo ("1. ", "2. ", "Passo ")
- Analisa imagens (quantidade, tamanho, proporção)
- Identifica padrões de texto puro (documentos normativos)

**Retorna**: `(tem_tela: bool, confianca: 0-1, razao: str)`

#### Nível 2: Vision Flash (Casos Ambíguos)
- Usado apenas quando a confiança está entre 0.3-0.7
- Resposta SIM/NÃO rápida
- Baixo custo de API

#### Nível 3: Vision Pro (Análise Completa)
- Usado quando há tela confirmada
- Gera instruções passo a passo detalhadas
- Extrai elementos visuais, campos de formulário
- Usa nomes EXATOS dos elementos do sistema

### 4. Montagem do JSON

O JSON final contém:

```json
{
  "id": "documento_pagina_001",
  "chunk_text": "Texto combinado (instruções + texto original)",
  "document_title": "Título do Documento",
  "source_file": "arquivo.pdf",
  "task_title": "Título da Tarefa/Tela",
  "chunk_type": "contexto|texto|interface",
  "pagina": 1,
  "num_palavras": 500,
  "tipo_tela": "listagem|formulário|documento|...",
  "num_elementos": 5,
  "tem_texto": true,
  "tem_instrucoes_navegacao": true
}
```

---

## 🎯 Detecção Híbrida de Telas

### Como Funciona

```
Para cada página:
1. Extrair texto e imagens
2. Executar heurística local (sem API)
   ├─ Alta confiança tem tela (≥0.7) → Vision Pro
   ├─ Alta confiança sem tela (≥0.7) → Pula Vision
   ├─ Confiança média (0.3-0.7) → Vision Flash para confirmar
   └─ Baixa confiança (<0.3) → Pula Vision (texto puro)
3. Se ambíguo: Vision Flash confirma
   ├─ Confirma tela → Vision Pro
   └─ Rejeita tela → Pula Vision
4. Vision Pro gera instruções completas
```

### Economia

Para um documento de 12 páginas apenas textual:
- **Sem detecção**: 12 chamadas Vision = ~5 min + 12× tokens
- **Com detecção híbrida**: 0-2 chamadas Vision = ~15-30s + 0-2× tokens
- **Economia**: ~83-100% de chamadas Vision

---

## 💡 Exemplos

### Exemplo 1: Manual com Telas

```bash
# Processar manual do administrador (tem telas)
python processar_pdf_completo.py \
  documentos_para_processar/manual-administrador-negocial-pgd-petrvs.pdf \
  json_processados/manual-administrador-COMPLETO.json
```

**Saída esperada:**
```
📊 DETECÇÃO HÍBRIDA:
   Páginas com tela detectadas (heurística): 5
   Páginas sem tela detectadas (heurística): 0
   Páginas ambíguas → confirmadas com Vision: 2
   Páginas ambíguas → rejeitadas (sem tela): 0

🔍 PROCESSAMENTO VISION:
   Visão processada: 7 sucessos, 0 erros
```

### Exemplo 2: Documento Apenas Textual

```bash
# Processar portaria (apenas texto)
python processar_pdf_completo.py \
  documentos_para_processar/portaria-dnit-5283-2024.pdf \
  json_processados/portaria-COMPLETO.json
```

**Saída esperada:**
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

### Exemplo 3: Envio para Pinecone

```bash
# Enviar JSON gerado para Pinecone
python 2b_enviar_arquivo_especifico_pinecone.py \
  json_processados/manual-administrador-COMPLETO.json
```

---

## 📊 Formato do JSON Gerado

### Estrutura Completa

```json
[
  {
    "id": "manual_administrador_pagina_001",
    "chunk_text": "Título da Tela\n\nContexto da tela...\n\n1. Clicar em [Nome EXATO do botão]\n2. No campo [Nome EXATO], digitar...\n\n[Imagens da tela do sistema PETRVS com anotações]\n\nTexto original extraído do PDF...\n\n**Campos do Formulário:**\n- Campo (tipo, obrigatório)\n\n**Elementos da Tela:**\n- Elemento: ação (localização)\n\n**Observações:** ...",
    "document_title": "Manual Administrador Negocial Pgd Petrvs",
    "source_file": "manual-administrador-negocial-pgd-petrvs.pdf",
    "task_title": "Gerenciamento de Unidades",
    "chunk_type": "contexto",
    "pagina": 1,
    "num_palavras": 669,
    "tipo_tela": "listagem",
    "num_elementos": 2,
    "tem_texto": true,
    "tem_instrucoes_navegacao": true
  }
]
```

### Campos Explicados

- **id**: Identificador único do chunk
- **chunk_text**: Texto completo combinado (instruções + texto original)
- **document_title**: Título do documento
- **source_file**: Nome do arquivo PDF original
- **task_title**: Título da tarefa/tela
- **chunk_type**: Tipo do chunk (`contexto`, `texto`, `interface`)
- **pagina**: Número da página (1-indexed)
- **num_palavras**: Número de palavras no chunk
- **tipo_tela**: Tipo de tela detectado (`listagem`, `formulário`, `documento`, etc.)
- **num_elementos**: Número de elementos importantes na tela
- **tem_texto**: Se há texto extraído do PDF
- **tem_instrucoes_navegacao**: Se há instruções de navegação geradas

---

## 🔧 Configuração Avançada

### Ajustar Detecção Híbrida

No arquivo `processar_pdf_completo.py`, você pode ajustar:

```python
# Thresholds de confiança
CONFIANCA_ALTA = 0.7      # Decisão direta (heurística)
CONFIANCA_MEDIA = 0.3     # Usar Vision Flash para confirmar

# Parâmetros de heurística
MARCADORES_TELA = ['clicar em', 'botão', 'menu', ...]
TAMANHO_IMAGEM_GRANDE = (500, 300)  # Screenshots
```

### DPI de Imagens

```python
DPI_IMAGENS = 150  # Ajustar qualidade/resolução
```

### Retry de API

```python
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # Segundos
```

---

## 🧪 Testes

### Verificar Instalação

```bash
python -c "import fitz, google.generativeai, PIL; print('✅ Todas as dependências instaladas')"
```

### Processar Documento de Teste

```bash
# Use um PDF pequeno para teste
python processar_pdf_completo.py \
  documentos_para_processar/manual-informacoes-gerais-pgd-petrvs.pdf \
  json_processados/teste.json
```

---

## 📝 Changelog

### v1.0.0 (2025-01-26)
- ✅ Implementação inicial
- ✅ Detecção híbrida de telas
- ✅ Extração completa de texto
- ✅ Análise visual com Gemini Vision
- ✅ Suporte a documentos híbridos
- ✅ Integração com Pinecone

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 🆘 Suporte

Para problemas, dúvidas ou sugestões:

- Abra uma [Issue](https://github.com/seu-usuario/pgd-rag/issues)
- Entre em contato com a equipe de desenvolvimento

---

## 🙏 Agradecimentos

- Google Gemini Vision API
- PyMuPDF
- Pinecone
- Comunidade Python

---

**Desenvolvido com ❤️ para o Programa de Gestão e Desempenho (PGD) Petrvs**

