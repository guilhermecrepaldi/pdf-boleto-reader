"""
Gera calendário de contas a pagar organizado por data de vencimento.
Mostra os próximos 30 dias.
"""

# Author: Guilherme Crepaldi

from datetime import datetime, timedelta
from typing import List


def gerar_calendario(boletos: list, dias: int = 30) -> dict:
    """
    Organiza boletos por data de vencimento nos próximos N dias.
    Retorna dict { "YYYY-MM-DD": [lista de boletos] }.
    """
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    limite = hoje + timedelta(days=dias)

    calendario = {}
    for boleto in boletos:
        vencimento = boleto.get("vencimento")
        if not vencimento:
            continue
        try:
            data_venc = datetime.strptime(vencimento, "%d/%m/%Y")
        except (ValueError, TypeError):
            continue

        if hoje <= data_venc <= limite:
            chave = data_venc.strftime("%Y-%m-%d")
            if chave not in calendario:
                calendario[chave] = []
            calendario[chave].append(boleto)

    return dict(sorted(calendario.items()))


def exibir_calendario(calendario: dict):
    """
    Exibe o calendário no console com formatação legível.
    """
    if not calendario:
        print("📅 Nenhum boleto nos próximos 30 dias.")
        return

    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total = sum(len(v) for v in calendario.values())

    print(f"\n{'='*60}")
    print(f"  📅 CALENDÁRIO DE CONTAS A PAGAR — Próximos 30 dias")
    print(f"  Total: {total} boleto(s)")
    print(f"{'='*60}\n")

    for data_chave, boletos_dia in calendario.items():
        data_obj = datetime.strptime(data_chave, "%Y-%m-%d")
        dias_restantes = (data_obj - hoje).days
        nome_dia = data_obj.strftime("%A").capitalize()
        data_br = data_obj.strftime("%d/%m/%Y")

        # Emoji por urgência
        if dias_restantes == 0:
            emoji = "🔴 HOJE"
        elif dias_restantes <= 5:
            emoji = "🟡 Próx."
        else:
            emoji = "🟢"

        print(f"  {emoji}  {data_br} ({nome_dia}) — {dias_restantes} dia(s)")

        for boleto in boletos_dia:
            valor = boleto.get("valor", "---")
            nome = boleto.get("beneficiario", "Sem identificação")
            pago = " [PAGO]" if boleto.get("pago") else ""
            print(f"       R$ {valor} — {nome}{pago}")
        print()

    print(f"{'='*60}\n")
