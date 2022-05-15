"""
Configurações do Leitor de Boletos PDF.
"""

# Author: Guilherme Crepaldi

import os

# Diretórios e caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "boletos.db")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")

# Regex patterns (suportam a maioria dos bancos, mas não todos)
PATTERNS = {
    "valor": [
        r"R?\$?\s?(\d{1,3}(?:\.\d{3})*,\d{2})",
        r"VALOR\s*(?:TOTAL|DO\s*DOCUMENTO)?\s*:?\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
    ],
    "vencimento": [
        r"(\d{2}/\d{2}/\d{4})",
        r"VENCI[MC]ENTO\s*:?\s*(\d{2}/\d{2}/\d{4})",
        r"DATA\s*(?:DE\s*)?VENCI[MC]ENTO\s*:?\s*(\d{2}/\d{2}/\d{4})",
    ],
    "codigo_barras": [
        r"(\d{47})",
        r"(?:Codigo|Código|Linha\s*Digtável|Linha\s*Digitável)[:\s]*([\d\.\- ]+)",
    ],
    "beneficiario": [
        r"BENEFICI[ÁA]RIO\s*:?\s*(.+)",
        r"CEDENTE\s*:?\s*(.+)",
        r"FAVORECIDO\s*:?\s*(.+)",
        r"PAGADOR\s*:?\s*(.+)",
    ],
}

# Configurações de alerta
ALERTA_DIAS_AMARELO = 5  # alerta amarelo para vencimentos próximos (até N dias)
ALERTA_VERMELHO_DIAS = 0  # vermelho para vencidos (0 = hoje pra trás)

# Email (opcional) — preencher se quiser alertas por email
EMAIL_CONFIG = {
    "smtp_server": os.getenv("BOLETO_SMTP_SERVER", ""),
    "smtp_port": int(os.getenv("BOLETO_SMTP_PORT", "587")),
    "email_from": os.getenv("BOLETO_EMAIL_FROM", ""),
    "email_to": os.getenv("BOLETO_EMAIL_TO", ""),
    "username": os.getenv("BOLETO_EMAIL_USER", ""),
    "password": os.getenv("BOLETO_EMAIL_PASS", ""),
}
