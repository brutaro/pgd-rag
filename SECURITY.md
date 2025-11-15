# Política de Segurança

## 🔒 Proteção de Credenciais

Este documento descreve as medidas de segurança implementadas para proteger credenciais e informações sensíveis.

---

## ⚠️ CRÍTICO: NUNCA COMMITE

Os seguintes arquivos **NUNCA** devem ser commitados no repositório:

### Arquivos de Ambiente
- `.env` e todas as variações (`.env.local`, `.env.production`, etc.)
- Qualquer arquivo que contenha `*.env` no nome
- Arquivos com extensões de chaves: `*.key`, `*.pem`, `*.p12`, `*.pfx`

### Arquivos com Nomes Sensíveis
- Qualquer arquivo com `*secret*` no nome
- Qualquer arquivo com `*credential*` no nome
- Qualquer arquivo com `*password*` no nome
- Pastas `secrets/` e `credentials/`

### Outros Arquivos Sensíveis
- Bancos de dados: `*.db`, `*.sqlite`, `*.sqlite3`
- Logs que possam conter informações: `*.log`
- Cache que possa conter dados: `*.cache`

---

## ✅ Verificações Antes de Commitar

### 1. Verificar Status do Git

```bash
git status
```

**Certifique-se de que:**
- ❌ `.env` **NÃO** aparece na lista
- ❌ Nenhum arquivo com `*.key`, `*.pem` aparece
- ❌ Nenhum arquivo com `secret` ou `credential` no nome aparece

### 2. Verificar Conteúdo dos Arquivos

Se você modificou algum arquivo Python, verifique se não há chaves hardcoded:

```bash
# Verificar se há chaves hardcoded
grep -r "AIza[0-9A-Za-z_-]\{35\}" *.py
grep -r "sk-[0-9A-Za-z]\{48,\}" *.py
grep -r "api_key\s*=\s*['\"][^'\"]" *.py
```

**Se encontrar algo, REMOVA antes de commitar!**

### 3. Verificar .gitignore

Certifique-se de que o `.gitignore` está atualizado:

```bash
# Verificar se .env está ignorado
git check-ignore .env
# Deve retornar: .env
```

---

## 🔐 Boas Práticas

### ✅ FAZER:

1. **Sempre use variáveis de ambiente** para credenciais
2. **Use o arquivo `env.example`** como template
3. **Verifique `git status`** antes de cada commit
4. **Revise as mudanças** com `git diff` antes de commitar
5. **Use `os.getenv()`** no código Python (não hardcode)

### ❌ NÃO FAZER:

1. ❌ **NUNCA** commite arquivos `.env` com chaves reais
2. ❌ **NUNCA** hardcode chaves no código Python
3. ❌ **NUNCA** commite certificados ou chaves privadas
4. ❌ **NUNCA** commite logs que possam conter informações sensíveis
5. ❌ **NUNCA** commite backups de arquivos com credenciais

---

## 🚨 Se Você Acidentalmente Commitou Credenciais

### Ação Imediata:

1. **Revogue as credenciais comprometidas imediatamente:**
   - Google Gemini: Gere nova chave em https://makersuite.google.com/app/apikey
   - Pinecone: Gere nova chave em https://app.pinecone.io/

2. **Remova do histórico do Git:**
   ```bash
   # Se ainda não fez push
   git reset HEAD~1
   
   # Se já fez push, use git filter-branch ou BFG Repo-Cleaner
   # Consulte: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
   ```

3. **Force push (apenas se necessário e com cuidado):**
   ```bash
   git push --force
   ```

4. **Notifique a equipe** se for um repositório compartilhado

---

## 📋 Checklist de Segurança

Antes de cada commit, verifique:

- [ ] `.env` não está na lista de arquivos modificados
- [ ] Nenhuma chave está hardcoded no código
- [ ] `git status` não mostra arquivos sensíveis
- [ ] `config.py` usa apenas `os.getenv()`
- [ ] Nenhum arquivo com extensão `.key`, `.pem`, `.p12` está sendo commitado
- [ ] Logs não contêm informações sensíveis

---

## 🔍 Verificação Automática

O arquivo `.gitignore` está configurado para proteger automaticamente:

```gitignore
# Environment variables and secrets (CRÍTICO - NUNCA COMMITAR)
.env
.env.*
*.env
*.key
*.pem
*secret*
*credential*
*password*
secrets/
credentials/
```

---

## 📞 Suporte

Se você encontrar ou suspeitar de um vazamento de credenciais:

1. **Revogue as credenciais imediatamente**
2. **Abra uma issue** no repositório (se for público)
3. **Entre em contato** com a equipe de segurança

---

**Lembre-se: Segurança é responsabilidade de todos! 🔒**

