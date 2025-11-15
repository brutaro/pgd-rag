#!/bin/bash
# Script de verificação de segurança antes de commit

echo "🔒 VERIFICAÇÃO DE SEGURANÇA"
echo "============================"
echo ""

ERROS=0

# 1. Verificar se .env está no .gitignore
echo "1. Verificando .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo "   ✅ .env está no .gitignore"
else
    echo "   ❌ ERRO: .env NÃO está no .gitignore!"
    ERROS=$((ERROS + 1))
fi

# 2. Verificar se há chaves hardcoded
echo ""
echo "2. Verificando chaves hardcoded..."
if grep -rE "(AIza[0-9A-Za-z_-]{35}|sk-[0-9A-Za-z]{48,}|api_key\s*=\s*['\"][^'\"]+)" *.py 2>/dev/null | grep -v "os.getenv\|config\." | grep -v "#"; then
    echo "   ❌ ERRO: Chaves hardcoded encontradas!"
    grep -rE "(AIza[0-9A-Za-z_-]{35}|sk-[0-9A-Za-z]{48,})" *.py 2>/dev/null | grep -v "os.getenv\|config\."
    ERROS=$((ERROS + 1))
else
    echo "   ✅ Nenhuma chave hardcoded encontrada"
fi

# 3. Verificar se .env existe e tem conteúdo
echo ""
echo "3. Verificando arquivo .env..."
if [ -f .env ]; then
    if [ -s .env ]; then
        echo "   ⚠️  .env existe e tem conteúdo (OK se não for commitado)"
        if grep -q "sua_chave\|exemplo\|example" .env 2>/dev/null; then
            echo "   ⚠️  .env contém valores de exemplo - substitua por chaves reais"
        fi
    else
        echo "   ℹ️  .env existe mas está vazio"
    fi
else
    echo "   ℹ️  .env não existe (criar a partir de env.example)"
fi

# 4. Verificar se config.py usa os.getenv
echo ""
echo "4. Verificando config.py..."
if grep -q "os.getenv" config.py; then
    echo "   ✅ config.py usa os.getenv() (seguro)"
else
    echo "   ❌ ERRO: config.py não usa os.getenv()!"
    ERROS=$((ERROS + 1))
fi

# Resultado final
echo ""
echo "============================"
if [ $ERROS -eq 0 ]; then
    echo "✅ SEGURANÇA: Tudo OK!"
    echo ""
    echo "📋 Próximos passos:"
    echo "   1. git status (verificar que .env não aparece)"
    echo "   2. git add ."
    echo "   3. git commit -m 'feat: ...'"
    exit 0
else
    echo "❌ ERROS ENCONTRADOS: $ERROS"
    echo ""
    echo "⚠️  CORRIJA OS ERROS ANTES DE COMMITAR!"
    exit 1
fi
