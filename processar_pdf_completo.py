#!/usr/bin/env python3
"""
Script unificado para processar PDFs completos:
1. Transforma cada página em imagem
2. Extrai texto com Python
3. Processa telas com Gemini Vision (opcional)
4. Monta JSON final com metadados pronto para ingestão
"""
import fitz  # PyMuPDF
import google.generativeai as genai
from PIL import Image
import json
import os
import sys
import io
import time
from tqdm import tqdm
import config

# --- CONFIGURAÇÕES ---
MODELO_VISION = "gemini-2.5-flash"
DPI_IMAGENS = 150
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2
DELAY_ENTRE_PAGINAS = 1.5

# Prompt para análise de telas - Traduzir telas em texto inteligível usando nomes EXATOS dos elementos
PROMPT_VISION = """Analise esta tela do sistema PGD Petrvs e traduza os elementos visuais em instruções passo a passo claras.

REGRAS FUNDAMENTAIS:
1. Use os nomes EXATOS dos botões, menus e campos como aparecem na tela
2. Se houver números ou setas indicando passos, siga a ordem exata mostrada
3. Seja específico sobre ONDE clicar usando os nomes exatos dos elementos
4. Organize as instruções na ordem lógica de uso

FORMATO JSON (responda APENAS o JSON, sem texto adicional):
{
  "titulo_tela": "Título ou ação principal da tela",
  "tipo_tela": "listagem/formulário/modal/dashboard/navegação/documento/início",
  "contexto": "O que esta tela faz e quando é usada",
  "instrucoes_navegacao": [
    "1. Clicar em [Nome EXATO do botão/menu como aparece na tela]",
    "2. No campo [Nome EXATO do campo], digitar/selecionar [o que esperado]",
    "3. Clicar em [Nome EXATO do botão]",
    "..."
  ],
  "elementos_visiveis": [
    {
      "tipo": "menu/botão/campo/tabela/card/ícone",
      "nome": "Texto EXATO visível na tela",
      "localizacao": "Onde está (ex: 'menu superior', 'botão no canto direito', 'card central')",
      "acao": "O que fazer com este elemento (ex: 'Clicar para abrir listagem', 'Digitar texto', 'Selecionar opção')"
    }
  ],
  "campos_formulario": [
    {
      "nome": "Nome EXATO do campo como aparece na tela",
      "tipo": "texto/numérico/data/dropdown/checkbox",
      "obrigatorio": true/false,
      "formato": "Formato esperado se houver (ex: dd/mm/aaaa)"
    }
  ],
  "observacoes": "Informações importantes, validações ou dicas de uso"
}

CRÍTICO: 
- Use SEMPRE os textos EXATOS visíveis na tela (não invente, não generalize, não use sinônimos)
- Se o botão diz "Incluir", escreva "Incluir" (não "Adicionar" ou "Criar")
- Se o menu diz "Planejamento", escreva "Planejamento" (não "Planejamento de Trabalho" ou outro)
- Se há números 1, 2, 3 na tela, use-os na mesma ordem"""

# Prompt para detecção rápida de telas (usado apenas em casos ambíguos)
PROMPT_DETECCAO_TELA = """Esta imagem contém uma tela de sistema/aplicação com elementos interativos (botões, menus, campos, formulários)?

Responda APENAS "SIM" ou "NÃO"."""

def detectar_se_tem_tela_heuristica(texto_pagina, imagens_pagina, pixmap, documento):
    """
    Detecta se a página contém telas de sistema usando heurísticas locais (sem API).
    
    Retorna: (tem_tela: bool, confianca: float 0-1, razao: str)
    """
    if not texto_pagina and len(imagens_pagina) == 0:
        return (False, 1.0, "Página vazia")
    
    # 1. Verificar marcadores de tela no texto
    marcadores_tela = [
        'clicar em', 'clicar no', 'clicar na',
        'selecionar', 'selecionar o', 'selecionar a',
        'botão', 'menu', 'campo', 'formulário',
        'tela do sistema', 'sistema', 'petrvs',
        'incluir', 'editar', 'excluir', 'gravar', 'cancelar',
        'filtrar', 'buscar', 'pesquisar',
        'menu superior', 'menu lateral',
        'ícone', 'aba', 'dropdown'
    ]
    
    texto_lower = texto_pagina.lower()
    marcadores_encontrados = sum(1 for marcador in marcadores_tela if marcador in texto_lower)
    
    # 2. Verificar instruções passo a passo
    tem_passos = any(marker in texto_pagina for marker in ['1. ', '2. ', '3. ', 'Passo ', 'passo '])
    
    # 3. Verificar quantidade e tamanho de imagens
    qtd_imagens = len(imagens_pagina)
    imagens_grandes = 0
    imagens_medias = 0
    
    for img in imagens_pagina:
        # Obter dimensões da imagem
        xref = img[0]
        try:
            base_image = documento.extract_image(xref)
            width = base_image['width']
            height = base_image['height']
            
            # Screenshots de telas geralmente têm dimensões específicas
            if width > 500 and height > 300:
                imagens_grandes += 1
            elif width > 200 and height > 150:
                imagens_medias += 1
        except:
            pass
    
    # 4. Verificar proporção texto/imagem
    tamanho_pagina = pixmap.width * pixmap.height
    razao_texto_imagem = len(texto_pagina) / max(tamanho_pagina / 1000, 1)
    
    # 5. Calcular pontuação e confiança
    pontuacao = 0
    razoes = []
    
    # Marcadores de tela no texto (+0.3 por marcador, até +1.5)
    if marcadores_encontrados > 0:
        pontos_marcadores = min(marcadores_encontrados * 0.3, 1.5)
        pontuacao += pontos_marcadores
        razoes.append(f"{marcadores_encontrados} marcadores de tela no texto")
    
    # Instruções passo a passo (+0.8)
    if tem_passos:
        pontuacao += 0.8
        razoes.append("instruções passo a passo")
    
    # Imagens grandes (screenshots) (+0.5 cada, até +1.5)
    if imagens_grandes > 0:
        pontos_imagens = min(imagens_grandes * 0.5, 1.5)
        pontuacao += pontos_imagens
        razoes.append(f"{imagens_grandes} imagem(ns) grande(s) (possível screenshot)")
    
    # Múltiplas imagens médias (+0.3 cada, até +1.0)
    if imagens_medias >= 2:
        pontos_medias = min((imagens_medias - 1) * 0.3, 1.0)
        pontuacao += pontos_medias
        razoes.append(f"{imagens_medias} imagens médias")
    
    # Proporção texto baixa + imagens (+0.4)
    if razao_texto_imagem < 0.1 and qtd_imagens > 0:
        pontuacao += 0.4
        razoes.append("baixa proporção texto/imagem")
    
    # 6. Penalidades (indicam texto puro)
    # Muito texto sem marcadores (-1.0)
    if len(texto_pagina) > 2000 and marcadores_encontrados == 0:
        pontuacao -= 1.0
        razoes.append("muito texto sem marcadores de tela")
    
    # Artigos, parágrafos, incisos (documento normativo) (-1.5)
    if any(marker in texto_pagina for marker in ['Art. ', '§ ', 'Parágrafo', 'CAPÍTULO', 'Seção']):
        if marcadores_encontrados < 3:  # Poucos marcadores de tela
            pontuacao -= 1.5
            razoes.append("padrão de documento normativo")
    
    # Nenhuma imagem (-0.5)
    if qtd_imagens == 0 and len(texto_pagina) > 500:
        pontuacao -= 0.5
        razoes.append("nenhuma imagem")
    
    # Normalizar pontuação para 0-1 (confiança)
    confianca = max(0.0, min(1.0, (pontuacao + 2.0) / 4.0))  # Escala de -2 a +2 → 0 a 1
    
    # Decisão: tem_tela se confiança > 0.5
    tem_tela = confianca > 0.5
    
    razao_str = "; ".join(razoes) if razoes else "sem indicadores claros"
    
    return (tem_tela, confianca, razao_str)

def confirmar_com_vision_flash(model, pixmap):
    """
    Confirma se há tela usando Vision Flash (rápido e barato).
    Usado apenas em casos ambíguos.
    
    Retorna: (tem_tela: bool, erro: str)
    """
    try:
        # Converter pixmap para PIL Image
        img_bytes = pixmap.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        
        # Redimensionar se necessário (para detecção rápida, menor resolução)
        if img.width > 800 or img.height > 800:
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Chamar Gemini Vision Flash apenas para SIM/NÃO
        response = model.generate_content([PROMPT_DETECCAO_TELA, img])
        resposta = response.text.strip().upper()
        
        # Verificar resposta
        if "SIM" in resposta:
            return (True, None)
        else:
            return (False, None)
            
    except Exception as e:
        return (None, str(e))

def configurar_gemini():
    """Configura o Gemini API"""
    genai.configure(api_key=config.GEMINI_API_KEY)
    return genai.GenerativeModel(MODELO_VISION)

def processar_tela_com_retry(model, pixmap_image, max_retries=MAX_RETRIES):
    """Processa uma tela com retry logic"""
    
    for tentativa in range(max_retries):
        try:
            # Converter pixmap para PIL Image
            img_bytes = pixmap_image.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            
            # Redimensionar se necessário
            if img.width > 1500 or img.height > 1500:
                img.thumbnail((1500, 1500), Image.Resampling.LANCZOS)
            
            # Chamar Gemini Vision
            response = model.generate_content([PROMPT_VISION, img])
            texto = response.text.strip()
            
            # Limpar markdown
            if "```json" in texto:
                texto = texto.split("```json")[1].split("```")[0].strip()
            elif "```" in texto:
                texto = texto.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            analise = json.loads(texto)
            return analise, None  # Sucesso
            
        except json.JSONDecodeError as e:
            erro = f"JSON inválido: {str(e)[:100]}"
            if tentativa < max_retries - 1:
                delay = RETRY_DELAY_BASE * (2 ** tentativa)
                time.sleep(delay)
            else:
                return None, erro
                
        except Exception as e:
            erro = str(e)[:100]
            if "429" in erro or "quota" in erro.lower() or "rate" in erro.lower():
                delay = 10 * (2 ** tentativa)
                if tentativa < max_retries - 1:
                    time.sleep(delay)
                else:
                    return None, f"Rate limit após {max_retries} tentativas"
            else:
                if tentativa < max_retries - 1:
                    delay = RETRY_DELAY_BASE * (2 ** tentativa)
                    time.sleep(delay)
                else:
                    return None, erro
    
    return None, "Máximo de tentativas excedido"

def processar_pdf_completo(caminho_pdf, output_json, processar_telas=True):
    """
    Processa um PDF completo: extrai texto, imagens e processa com Vision
    
    Args:
        caminho_pdf: Caminho para o PDF
        output_json: Caminho para o JSON de saída
        processar_telas: Se True, processa telas com Gemini Vision
    """
    print("="*80)
    print("PROCESSAMENTO COMPLETO DE PDF")
    print("="*80)
    print(f"\n📄 PDF: {os.path.basename(caminho_pdf)}")
    print(f"📁 Saída: {output_json}")
    print(f"🖼️  Processar telas: {'Sim' if processar_telas else 'Não'}\n")
    
    # Abrir PDF
    documento = fitz.open(caminho_pdf)
    total_paginas = len(documento)
    
    if total_paginas == 0:
        print("❌ PDF vazio!")
        documento.close()
        return
    
    print(f"📊 Total de páginas: {total_paginas}\n")
    
    # Configurar Gemini se necessário
    modelo_vision = None
    if processar_telas:
        print("Configurando Gemini Vision...")
        modelo_vision = configurar_gemini()
        print(f"✅ Modelo: {MODELO_VISION}\n")
    
    # Extrair nome do documento
    nome_base = os.path.splitext(os.path.basename(caminho_pdf))[0]
    document_title = nome_base.replace('-', ' ').title()
    
    # Processar cada página
    documentos = []
    sucessos_vision = 0
    erros_vision = 0
    paginas_com_tela = 0
    paginas_sem_tela = 0
    paginas_ambigua_confirmada = 0
    paginas_ambigua_rejeitada = 0
    
    print("Processando páginas...")
    print("-"*80)
    
    for num_pagina in tqdm(range(total_paginas), desc="Processando", unit="página"):
        pagina = documento.load_page(num_pagina)
        
        # 1. Extrair texto
        texto_pagina = pagina.get_text("text").strip()
        
        # 2. Extrair imagens da página
        imagens_pagina = pagina.get_images()
        
        # 3. Converter página em imagem (pixmap)
        pixmap = pagina.get_pixmap(dpi=DPI_IMAGENS)
        
        # 4. DETECÇÃO HÍBRIDA: Verificar se há tela antes de chamar Vision
        analise_vision = None
        usar_vision = False
        
        if processar_telas and modelo_vision:
            # Etapa 1: Heurística rápida (sem API)
            tem_tela, confianca, razao = detectar_se_tem_tela_heuristica(
                texto_pagina, imagens_pagina, pixmap, documento
            )
            
            # Decisão baseada em confiança
            if confianca >= 0.7:  # Alta confiança
                if tem_tela:
                    # Confiança alta de que tem tela → usar Vision
                    usar_vision = True
                    paginas_com_tela += 1
                else:
                    # Confiança alta de que NÃO tem tela → pular Vision
                    usar_vision = False
                    paginas_sem_tela += 1
            
            elif confianca < 0.7 and confianca >= 0.3:  # Confiança média (ambíguo)
                # Caso ambíguo → usar Vision Flash para confirmar
                tem_tela_confirmada, erro_conf = confirmar_com_vision_flash(modelo_vision, pixmap)
                
                if erro_conf:
                    # Se erro na confirmação, usar Vision completo por segurança
                    usar_vision = True
                    paginas_ambigua_confirmada += 1
                elif tem_tela_confirmada:
                    # Confirmado que tem tela → usar Vision completo
                    usar_vision = True
                    paginas_ambigua_confirmada += 1
                else:
                    # Confirmado que NÃO tem tela → pular Vision
                    usar_vision = False
                    paginas_ambigua_rejeitada += 1
            
            else:  # Confiança muito baixa (< 0.3) - provavelmente texto puro
                usar_vision = False
                paginas_sem_tela += 1
            
            # Etapa 2: Usar Vision apenas se necessário
            if usar_vision:
                analise_vision, erro = processar_tela_com_retry(modelo_vision, pixmap)
                
                if analise_vision:
                    sucessos_vision += 1
                else:
                    erros_vision += 1
                    if erro:
                        tqdm.write(f"⚠️  Página {num_pagina + 1}: {erro}")
        
        # 4. Montar chunk_text combinado (priorizando texto com instruções)
        chunk_text = ""
        
        # Priorizar texto extraído se já tiver instruções passo a passo
        tem_instrucoes_texto = texto_pagina and (
            any(marker in texto_pagina for marker in ['1. ', '2. ', '3. ', 'Passo ', 'Clicar em', 'Selecionar'])
        )
        
        # Se há análise visual, usar para enriquecer ou substituir
        if analise_vision:
            titulo_tela = analise_vision.get('titulo_tela', '')
            contexto = analise_vision.get('contexto', '')
            instrucoes_nav = analise_vision.get('instrucoes_navegacao', [])
            elementos = analise_vision.get('elementos_visiveis', [])
            campos = analise_vision.get('campos_formulario', [])
            observacoes = analise_vision.get('observacoes', '')
            
            # Se a análise visual gerou instruções, priorizar ela
            if instrucoes_nav and isinstance(instrucoes_nav, list):
                chunk_text = titulo_tela + "\n\n" if titulo_tela else ""
                
                if contexto:
                    chunk_text += f"{contexto}\n\n"
                
                # Adicionar instruções passo a passo (principal)
                chunk_text += "\n".join(instrucoes_nav) + "\n\n"
                
                # Se texto extraído tem informações adicionais, adicionar
                if texto_pagina and not tem_instrucoes_texto:
                    chunk_text += f"[Imagens da tela do sistema PETRVS com anotações]\n\n"
                    chunk_text += f"{texto_pagina}\n\n"
                
                # Adicionar campos do formulário se houver
                if campos:
                    chunk_text += "**Campos do Formulário:**\n"
                    for campo in campos:
                        nome = campo.get('nome', '')
                        tipo = campo.get('tipo', '')
                        obrig = "obrigatório" if campo.get('obrigatorio') else "opcional"
                        formato = campo.get('formato', '')
                        chunk_text += f"- {nome} ({tipo}, {obrig}"
                        if formato:
                            chunk_text += f", formato: {formato}"
                        chunk_text += ")\n"
                    chunk_text += "\n"
                
                # Adicionar elementos visíveis da tela
                if elementos:
                    chunk_text += "**Elementos da Tela:**\n"
                    for elem in elementos:
                        nome = elem.get('nome', '')
                        acao = elem.get('acao', '')
                        local = elem.get('localizacao', '')
                        chunk_text += f"- {nome}"
                        if acao:
                            chunk_text += f": {acao}"
                        if local:
                            chunk_text += f" ({local})"
                        chunk_text += "\n"
                    chunk_text += "\n"
                
                if observacoes:
                    chunk_text += f"**Observações:** {observacoes}\n"
                    
            else:
                # Fallback: usar estrutura antiga se não houver instruções_navegacao
                chunk_text = texto_pagina if texto_pagina else ""
                if contexto:
                    chunk_text += f"\n\nContexto: {contexto}\n"
        
        # Se não há análise visual ou ela não gerou instruções, usar texto extraído
        elif texto_pagina:
            chunk_text = texto_pagina
            if tem_instrucoes_texto:
                # Adicionar marcador de imagem se houver instruções mas não análise visual
                chunk_text = chunk_text.replace(
                    "[Imagem", "[Imagens da tela do sistema PETRVS com anotações]"
                ) if "[Imagem" in chunk_text else f"[Imagens da tela do sistema PETRVS com anotações]\n\n{chunk_text}"
        
        # Se não há conteúdo, pular
        if not chunk_text.strip():
            continue
        
        # 5. Criar documento final
        doc_id = f"{nome_base.replace('-', '_')}_pagina_{num_pagina + 1:03d}"
        
        # Determinar tipo de chunk (usar "contexto" para instruções de navegação)
        if analise_vision:
            # Se tem instruções de navegação, é contexto (como no JSON original)
            instrucoes_nav = analise_vision.get('instrucoes_navegacao', [])
            if instrucoes_nav:
                chunk_type = "contexto"
            else:
                chunk_type = "interface"
            task_title = analise_vision.get('titulo_tela', f'Página {num_pagina + 1}')
        elif tem_instrucoes_texto:
            # Texto com instruções também é contexto
            chunk_type = "contexto"
            # Extrair primeiro título do texto
            linhas = texto_pagina.split('\n')[:3]
            task_title = linhas[0].strip() if linhas else f'Página {num_pagina + 1}'
            # Remover marcações de formatação
            task_title = task_title.replace('**', '').strip()
            if len(task_title) > 100:
                task_title = task_title[:100] + "..."
        else:
            chunk_type = "texto"
            # Extrair primeiro título/parágrafo do texto como task_title
            linhas = texto_pagina.split('\n')[:3]
            task_title = linhas[0].strip() if linhas else f'Página {num_pagina + 1}'
            task_title = task_title.replace('**', '').strip()
            if len(task_title) > 100:
                task_title = task_title[:100] + "..."
        
        doc = {
            'id': doc_id,
            'chunk_text': chunk_text.strip(),
            'document_title': document_title,
            'source_file': os.path.basename(caminho_pdf),
            'task_title': task_title,
            'chunk_type': chunk_type,
            'pagina': num_pagina + 1,
            'num_palavras': len(chunk_text.split()),
        }
        
        # Adicionar metadados de tela se houver
        if analise_vision:
            doc['tipo_tela'] = analise_vision.get('tipo_tela', 'N/A')
            elementos_importantes = analise_vision.get('elementos_importantes', [])
            campos_formulario = analise_vision.get('campos_formulario', [])
            doc['num_elementos'] = len(elementos_importantes) + len(campos_formulario)
            doc['tem_texto'] = bool(texto_pagina)
            doc['tem_instrucoes_navegacao'] = bool(analise_vision.get('instrucoes_navegacao', []))
        else:
            doc['tem_texto'] = bool(texto_pagina)
            doc['tem_instrucoes_navegacao'] = tem_instrucoes_texto
        
        documentos.append(doc)
        
        # Delay entre páginas
        if processar_telas:
            time.sleep(DELAY_ENTRE_PAGINAS)
    
    documento.close()
    
    # Salvar JSON final
    os.makedirs(os.path.dirname(output_json) if os.path.dirname(output_json) else '.', exist_ok=True)
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(documentos, f, ensure_ascii=False, indent=2)
    
    # Resumo
    print("\n" + "="*80)
    print("PROCESSAMENTO CONCLUÍDO")
    print("="*80)
    print(f"✅ Total de documentos criados: {len(documentos)}")
    if processar_telas:
        print(f"\n📊 DETECÇÃO HÍBRIDA:")
        print(f"   Páginas com tela detectadas (heurística): {paginas_com_tela}")
        print(f"   Páginas sem tela detectadas (heurística): {paginas_sem_tela}")
        print(f"   Páginas ambíguas → confirmadas com Vision: {paginas_ambigua_confirmada}")
        print(f"   Páginas ambíguas → rejeitadas (sem tela): {paginas_ambigua_rejeitada}")
        print(f"\n🔍 PROCESSAMENTO VISION:")
        print(f"   Visão processada: {sucessos_vision} sucessos, {erros_vision} erros")
        total_vision_chamadas = sucessos_vision + erros_vision + paginas_ambigua_confirmada
        economia = total_paginas - total_vision_chamadas
        if economia > 0:
            print(f"   📉 Economia: {economia} página(s) sem chamadas Vision ({economia*100//total_paginas}%)")
    print(f"\n📝 Total de palavras: {sum(d['num_palavras'] for d in documentos):,}")
    print(f"📁 JSON salvo em: {output_json}")
    print("="*80 + "\n")
    
    return documentos

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python processar_pdf_completo.py <caminho_pdf> <output_json> [--sem-telas]")
        print("\nExemplos:")
        print("  python processar_pdf_completo.py manual.pdf json_processados/manual.json")
        print("  python processar_pdf_completo.py manual.pdf json_processados/manual.json --sem-telas")
        print("\nFlags:")
        print("  --sem-telas    Não processa telas com Gemini Vision (apenas extrai texto)")
        sys.exit(1)
    
    caminho_pdf = sys.argv[1]
    output_json = sys.argv[2]
    processar_telas = "--sem-telas" not in sys.argv
    
    if not os.path.exists(caminho_pdf):
        print(f"❌ Erro: PDF não encontrado: {caminho_pdf}")
        sys.exit(1)
    
    processar_pdf_completo(caminho_pdf, output_json, processar_telas)

