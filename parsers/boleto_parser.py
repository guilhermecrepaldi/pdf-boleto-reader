"""
Extração de texto de boletos em PDF usando pdfplumber.
Cada banco tem um layout diferente, isso funciona pra maioria mas não todos.
"""

# Author: Guilherme Crepaldi

import re
import pdfplumber


def extrair_texto(caminho_pdf: str) -> str:
    """
    Extrai todo o texto de um PDF usando pdfplumber.
    Retorna string única com todo o conteúdo textual.
    """
    texto = ""
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                conteudo = pagina.extract_text()
                if conteudo:
                    texto += conteudo + "\n"
    except Exception as e:
        raise RuntimeError(f"Erro ao abrir PDF '{caminho_pdf}': {e}")
    return texto.strip()


def extrair_valor(texto: str) -> str | None:
    """
    Tenta extrair o valor do boleto.
    Alguns boletos tem o valor no final do PDF, outros no meio.
    Tento varios padroes.
    """
    # Prioridade: padrão explícito de "VALOR TOTAL" etc.
    for padrao in [
        r"VALOR\s*(?:TOTAL|DO\s*DOCUMENTO)\s*:?\s*R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
        r"Total\s*:?\s*R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
        r"R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
    ]:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extrair_vencimento(texto: str) -> str | None:
    """
    Extrai data de vencimento no formato dd/mm/aaaa.
    Prioriza linhas com 'vencimento' explícito.
    """
    # Primeiro tenta padrão com label explícito
    for padrao_label in [
        r"VENCI[MC]ENTO\s*:?\s*(\d{2}/\d{2}/\d{4})",
        r"DATA\s*(?:DE\s*)?VENCI[MC]ENTO\s*:?\s*(\d{2}/\d{2}/\d{4})",
        r"Vencimento\s*:?\s*(\d{2}/\d{2}/\d{4})",
    ]:
        match = re.search(padrao_label, texto, re.IGNORECASE)
        if match:
            return match.group(1)

    # Fallback: qualquer data no formato dd/mm/aaaa
    # Filtra datas improváveis (ex: anos < 2020 ou > 2040)
    matches = re.findall(r"(\d{2}/\d{2}/\d{4})", texto)
    for data in matches:
        dia, mes, ano = data.split("/")
        if 2020 <= int(ano) <= 2040:
            return data

    return None


def extrair_codigo_barras(texto: str) -> str | None:
    """
    Extrai código de barras de 47 dígitos.
    Tenta primeiro linha digitável, depois sequência direta de 47 dígitos.
    """
    # Tenta extrair de "Linha Digitável" — remove pontuação e espaços
    for padrao_label in [
        r"(?:Linha\s*Digtável|Linha\s*Digitável|Codigo\s*[Bb]arras)[:\s]*([\d\.\- ]+)",
        r"(?:Código\s*[Bb]arras)[:\s]*([\d\.\- ]+)",
    ]:
        match = re.search(padrao_label, texto, re.IGNORECASE)
        if match:
            codigo_bruto = re.sub(r"[^\d]", "", match.group(1))
            if len(codigo_bruto) >= 44:
                return codigo_bruto[:47]  # pega os primeiros 47 dígitos

    # Fallback: qualquer sequência de 47 dígitos consecutivos
    match = re.search(r"(\d{47})", texto)
    if match:
        return match.group(1)

    return None


def extrair_beneficiario(texto: str) -> str | None:
    """
    Extrai nome do beneficiário/cedente.
    """
    for padrao in [
        r"BENEFICI[ÁA]RIO\s*:?\s*(.+)",
        r"CEDENTE\s*:?\s*(.+)",
        r"FAVORECIDO\s*:?\s*(.+)",
        r"PAGADOR\s*:?\s*(.+)",
    ]:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            nome = match.group(1).strip().rstrip(".")
            if nome:
                return nome
    return None


def parse_boleto(caminho_pdf: str) -> dict:
    """
    Parsing completo de um boleto PDF.
    Retorna dict com valor, vencimento, codigo_barras, beneficiario.
    """
    texto = extrair_texto(caminho_pdf)

    resultado = {
        "arquivo": caminho_pdf,
        "valor": extrair_valor(texto),
        "vencimento": extrair_vencimento(texto),
        "codigo_barras": extrair_codigo_barras(texto),
        "beneficiario": extrair_beneficiario(texto),
    }

    return resultado


def parse_texto_simulado(texto: str) -> dict:
    """
    Parsing a partir de texto simulado (modo --mock).
    Útil para testes sem PDF real.
    """
    resultado = {
        "arquivo": "(simulado)",
        "valor": extrair_valor(texto),
        "vencimento": extrair_vencimento(texto),
        "codigo_barras": extrair_codigo_barras(texto),
        "beneficiario": extrair_beneficiario(texto),
    }
    return resultado
