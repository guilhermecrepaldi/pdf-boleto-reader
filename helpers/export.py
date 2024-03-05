"""
Exporta boletos para CSV, JSON ou calendário PDF (via calendário texto/HTML).
"""

# Author: Guilherme Crepaldi

import csv
import json
import os
from datetime import datetime, timedelta
from typing import List


def exportar_csv(boletos: list, caminho: str = "boletos_exportados.csv") -> str:
    """
    Exporta lista de boletos para arquivo CSV.
    Retorna o caminho do arquivo gerado.
    """
    campos = ["id", "arquivo", "valor", "vencimento", "codigo_barras", "beneficiario", "lido_em", "pago"]

    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for boleto in boletos:
            linha = {campo: boleto.get(campo, "") for campo in campos}
            writer.writerow(linha)

    abs_path = os.path.abspath(caminho)
    print(f"  ✅ CSV exportado: {abs_path}")
    return abs_path


def exportar_json(boletos: list, caminho: str = "boletos_exportados.json") -> str:
    """
    Exporta lista de boletos para arquivo JSON.
    Retorna o caminho do arquivo gerado.
    """
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(boletos, f, ensure_ascii=False, indent=2)

    abs_path = os.path.abspath(caminho)
    print(f"  ✅ JSON exportado: {abs_path}")
    return abs_path


def exportar_calendario_html(boletos: list, caminho: str = "calendario_contas.html") -> str:
    """
    Gera um calendário visual em HTML com os boletos organizados por data.
    Retorna o caminho do arquivo gerado.
    """
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hoje_str = hoje.strftime("%d/%m/%Y %H:%M")

    # Organiza por data
    por_data = {}
    for b in boletos:
        v = b.get("vencimento")
        if not v:
            continue
        try:
            data_obj = datetime.strptime(v, "%d/%m/%Y")
        except ValueError:
            continue
        chave = data_obj.strftime("%Y-%m-%d")
        if chave not in por_data:
            por_data[chave] = []
        por_data[chave].append(b)

    por_data = dict(sorted(por_data.items()))

    # Monta HTML linha a linha pra evitar conflito de {} com format
    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html lang="pt-BR">')
    html_parts.append('<head>')
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append('<title>Calendário de Contas a Pagar</title>')
    html_parts.append('<style>')
    html_parts.append('  * { margin: 0; padding: 0; box-sizing: border-box; }')
    html_parts.append('  body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;')
    html_parts.append('         background: #f5f5f5; padding: 20px; color: #333; }')
    html_parts.append('  h1 { text-align: center; color: #1a1a2e; margin-bottom: 10px; }')
    html_parts.append('  .subtitle { text-align: center; color: #666; margin-bottom: 30px; }')
    html_parts.append('  .dia { background: white; border-radius: 10px; padding: 15px 20px;')
    html_parts.append('         margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);')
    html_parts.append('         border-left: 5px solid #4CAF50; }')
    html_parts.append('  .dia.vencido { border-left-color: #f44336; }')
    html_parts.append('  .dia.proximo { border-left-color: #ff9800; }')
    html_parts.append('  .dia.hoje { border-left-color: #2196F3; }')
    html_parts.append('  .dia h3 { font-size: 1.1em; color: #1a1a2e; margin-bottom: 8px; }')
    html_parts.append('  .boleto { padding: 5px 0; display: flex; justify-content: space-between; }')
    html_parts.append('  .boleto .valor { font-weight: bold; color: #1a1a2e; }')
    html_parts.append('  .boleto .beneficiario { color: #666; }')
    html_parts.append('  .boleto .pago { color: #4CAF50; font-weight: bold; }')
    html_parts.append('  .total { text-align: center; margin-top: 20px; font-size: 1.2em; color: #1a1a2e; }')
    html_parts.append('  footer { text-align: center; margin-top: 30px; color: #999; font-size: 0.9em; }')
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    html_parts.append(f'<h1>📅 Calendário de Contas a Pagar</h1>')
    html_parts.append(f'<p class="subtitle">Gerado em {hoje_str}</p>')

    total_boletos = 0
    total_valor = 0.0

    for data_chave, boletos_dia in por_data.items():
        data_obj = datetime.strptime(data_chave, "%Y-%m-%d")
        dias_restantes = (data_obj - hoje).days
        data_br = data_obj.strftime("%d/%m/%Y")
        nome_dia = data_obj.strftime("%A").capitalize()

        if dias_restantes < 0:
            classe = "vencido"
            tag = f"🔴 {abs(dias_restantes)} dia(s) atrasado"
        elif dias_restantes <= 5:
            classe = "proximo"
            tag = f"🟡 {dias_restantes} dia(s)"
        elif dias_restantes == 0:
            classe = "hoje"
            tag = "🔵 HOJE"
        else:
            classe = ""
            tag = f"🟢 {dias_restantes} dia(s)"

        html_parts.append(f'<div class="dia {classe}">')
        html_parts.append(f'  <h3>{data_br} ({nome_dia}) — {tag}</h3>')

        for b in boletos_dia:
            total_boletos += 1
            valor = b.get("valor", "---").replace(",", ".")
            try:
                total_valor += float(valor) if valor != "---" else 0
            except ValueError:
                pass

            pago = " [PAGO]" if b.get("pago") else ""
            html_parts.append('  <div class="boleto">')
            html_parts.append(f'    <span class="beneficiario">{b.get("beneficiario", "Sem identificação")}{pago}</span>')
            html_parts.append(f'    <span class="valor">R$ {b.get("valor", "---")}</span>')
            html_parts.append('  </div>')

        html_parts.append('</div>')

    html_parts.append(f'<div class="total">Total: {total_boletos} boleto(s) — R$ {total_valor:,.2f}</div>')
    html_parts.append('<footer>Gerado por PDF Boleto Reader</footer>')
    html_parts.append('</body>')
    html_parts.append('</html>')

    html = "\n".join(html_parts)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)

    abs_path = os.path.abspath(caminho)
    print(f"  ✅ Calendário HTML exportado: {abs_path}")
    return abs_path
