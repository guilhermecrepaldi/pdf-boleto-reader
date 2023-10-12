"""
Alertas de vencimento.
Compara vencimento com data atual:
  - Vermelho: vencidos
  - Amarelo: próximos 5 dias
  - Verde: ok
Opicionalmente envia email.
"""

# Author: Guilherme Crepaldi

import smtplib
import sys
from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

# Adiciona path para importar config (quando chamado como script)
sys.path.insert(0, "..")
from config import ALERTA_DIAS_AMARELO, EMAIL_CONFIG


def verificar_alertas(boletos: list) -> list:
    """
    Verifica cada boleto e retorna lista com status de alerta.
    Cada item: { "boleto": dict, "status": "vermelho"|"amarelo"|"verde", "dias_restantes": int }
    """
    hoje = date.today()
    resultados = []

    for boleto in boletos:
        vencimento_str = boleto.get("vencimento")
        if not vencimento_str:
            resultados.append({"boleto": boleto, "status": "sem_data", "dias_restantes": None})
            continue

        try:
            data_venc = datetime.strptime(vencimento_str, "%d/%m/%Y").date()
        except (ValueError, TypeError):
            resultados.append({"boleto": boleto, "status": "data_invalida", "dias_restantes": None})
            continue

        dias_restantes = (data_venc - hoje).days

        if dias_restantes < 0:
            status = "vermelho"
        elif dias_restantes <= ALERTA_DIAS_AMARELO:
            status = "amarelo"
        else:
            status = "verde"

        resultados.append({
            "boleto": boleto,
            "status": status,
            "dias_restantes": dias_restantes,
            "data_venc": vencimento_str,
        })

    return resultados


def exibir_alertas(resultados: list):
    """
    Exibe alertas no console com cores visuais (símbolos).
    """
    if not resultados:
        print("📭 Nenhum boleto para verificar.")
        return

    vermelhos = [r for r in resultados if r["status"] == "vermelho"]
    amarelos = [r for r in resultados if r["status"] == "amarelo"]
    verdes = [r for r in resultados if r["status"] == "verde"]

    print(f"\n{'='*60}")
    print("  🚨 ALERTAS DE VENCIMENTO")
    print(f"{'='*60}")

    if vermelhos:
        print(f"\n  🔴 VENCIDOS ({len(vermelhos)}):")
        for r in vermelhos:
            b = r["boleto"]
            print(f"     R$ {b.get('valor', '---')} — {b.get('beneficiario', '?')}")
            print(f"     Vencimento: {r['data_venc']} ({abs(r['dias_restantes'])} dia(s) atrasado)")
            print()

    if amarelos:
        print(f"\n  🟡 PRÓXIMOS (até {ALERTA_DIAS_AMARELO} dias):")
        for r in amarelos:
            b = r["boleto"]
            dias_str = "HOJE" if r["dias_restantes"] == 0 else f"{r['dias_restantes']} dia(s)"
            print(f"     R$ {b.get('valor', '---')} — {b.get('beneficiario', '?')}")
            print(f"     Vencimento: {r['data_venc']} ({dias_str})")
            print()

    if verdes:
        print(f"\n  🟢 DENTRO DO PRAZO ({len(verdes)}):")
        for r in verdes:
            b = r["boleto"]
            print(f"     R$ {b.get('valor', '---')} — {b.get('beneficiario', '?')} (venc. {r['data_venc']})")

    if not vermelhos and not amarelos:
        print("\n  ✅ Nenhum alerta urgente. Tudo em dia!")

    print(f"\n{'='*60}\n")


def enviar_email_alerta(resultados: list, destinatario: Optional[str] = None):
    """
    Envia alerta por email com a lista de boletos vencidos e próximos.
    Usa configuração do config.py.
    """
    cfg = EMAIL_CONFIG
    to_addr = destinatario or cfg.get("email_to")
    if not to_addr or not cfg.get("smtp_server"):
        print("  ⚠️  Email não configurado. Configure EMAIL_CONFIG em config.py")
        return False

    vermelhos = [r for r in resultados if r["status"] == "vermelho"]
    amarelos = [r for r in resultados if r["status"] == "amarelo"]

    corpo = "=== ALERTA DE BOLETOS ===\n\n"
    if vermelhos:
        corpo += f"🔴 VENCIDOS ({len(vermelhos)}):\n"
        for r in vermelhos:
            b = r["boleto"]
            corpo += f"  - R$ {b.get('valor', '---')} — {b.get('beneficiario', '?')} (venc. {r['data_venc']})\n"
        corpo += "\n"
    if amarelos:
        corpo += f"🟡 PRÓXIMOS ({len(amarelos)}):\n"
        for r in amarelos:
            b = r["boleto"]
            corpo += f"  - R$ {b.get('valor', '---')} — {b.get('beneficiario', '?')} (venc. {r['data_venc']})\n"

    try:
        msg = MIMEMultipart()
        msg["From"] = cfg.get("email_from", "")
        msg["To"] = to_addr
        msg["Subject"] = f"🚨 Alerta de Boletos — {len(vermelhos)} vencido(s), {len(amarelos)} próximo(s)"
        msg.attach(MIMEText(corpo, "plain", "utf-8"))

        with smtplib.SMTP(cfg["smtp_server"], int(cfg["smtp_port"])) as server:
            server.starttls()
            if cfg.get("username") and cfg.get("password"):
                server.login(cfg["username"], cfg["password"])
            server.send_message(msg)

        print(f"  ✅ Email enviado para {to_addr}")
        return True
    except Exception as e:
        print(f"  ❌ Erro ao enviar email: {e}")
        return False
