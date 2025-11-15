# Comandos Git para Commit e Push

## 📋 Pré-requisitos

1. Certifique-se de que o Git está configurado:
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

2. Crie o repositório no GitHub (se ainda não existe):
   - Acesse https://github.com
   - Clique em "New repository"
   - Nome: `pgd-rag`
   - Descrição: "Sistema de processamento de PDFs para RAG do PGD Petrvs"
   - Público ou Privado (sua escolha)
   - **NÃO** inicialize com README, .gitignore ou LICENSE (já temos)

## 🚀 Inicializar Repositório (Primeira Vez)

```bash
cd /Users/brutx/Documents/projects/pgd-rag

# Inicializar Git
git init

# Adicionar remote (substitua seu-usuario pelo seu usuário GitHub)
git remote add origin https://github.com/seu-usuario/pgd-rag.git

# Verificar remote
git remote -v
```

## 📝 Preparar Commit

```bash
# Ver status dos arquivos
git status

# Adicionar todos os arquivos (exceto os ignorados pelo .gitignore)
git add .

# Ver o que será commitado
git status
```

## 💾 Fazer Commit

```bash
# Commit inicial
git commit -m "feat: Implementação inicial do sistema PGD RAG

- Script principal de processamento de PDFs (processar_pdf_completo.py)
- Detecção híbrida de telas (heurística + Vision)
- Extração de texto e análise visual com Gemini Vision
- Script de envio para Pinecone (2b_enviar_arquivo_especifico_pinecone.py)
- Documentação completa (README, CONTRIBUTING, EXEMPLOS)
- Configuração completa (requirements.txt, .gitignore, CI/CD)

Features:
- Processamento completo de PDFs
- Detecção inteligente de telas de sistema
- Economia de API com detecção híbrida
- Instruções passo a passo detalhadas
- Suporte a documentos híbridos (texto + telas)"

# Ou commit mais simples
git commit -m "feat: Sistema completo de processamento de PDFs para RAG"
```

## 🚀 Push para GitHub

```bash
# Primeira vez (branch main)
git branch -M main
git push -u origin main

# Commits subsequentes
git push
```

## 📋 Estrutura do Commit Inicial

O commit inicial deve incluir:

### ✅ Arquivos Principais:
- `processar_pdf_completo.py` - Script principal
- `2b_enviar_arquivo_especifico_pinecone.py` - Script Pinecone
- `config.py` - Configurações

### ✅ Documentação:
- `README.md` - Documentação principal
- `CONTRIBUTING.md` - Guia de contribuição
- `EXEMPLOS.md` - Exemplos práticos
- `LICENSE` - Licença MIT

### ✅ Configuração:
- `requirements.txt` - Dependências
- `.gitignore` - Arquivos ignorados
- `.github/workflows/ci.yml` - CI/CD

### ❌ NÃO Commitar:
- `.env` - Variáveis de ambiente (sensíveis)
- `venv/` - Ambiente virtual
- `__pycache__/` - Cache Python
- `json_processados/` - JSONs gerados
- `*.pdf` - PDFs grandes
- `RELATORIO_*.md` - Relatórios gerados

## 🔄 Workflow de Desenvolvimento

### Para novos commits:

```bash
# 1. Verificar status
git status

# 2. Adicionar arquivos modificados
git add <arquivo>  # ou git add . para tudo

# 3. Commit com mensagem descritiva
git commit -m "tipo: descrição curta

Descrição detalhada do que foi alterado"

# 4. Push
git push
```

### Tipos de commit (convenção):

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Mudanças na documentação
- `style:` - Formatação, ponto-e-vírgula faltando, etc
- `refactor:` - Refatoração de código
- `test:` - Adicionar ou modificar testes
- `chore:` - Mudanças em build, ferramentas, etc

## 🔍 Verificar Antes do Push

```bash
# Ver diferenças
git diff

# Ver histórico de commits
git log --oneline

# Verificar arquivos rastreados
git ls-files
```

## 🐛 Solução de Problemas

### Erro: "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/seu-usuario/pgd-rag.git
```

### Erro: "Updates were rejected"
```bash
git pull origin main --rebase
git push
```

### Desfazer último commit (antes do push)
```bash
git reset --soft HEAD~1
```

---

**Pronto para GitHub! 🚀**
