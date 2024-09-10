#!/usr/bin/env python3
"""
Boleto Reader — CLI principal.
Leitor de boletos em PDF que extrai informacoes como valor,
data de vencimento, codigo de barras, beneficiario.
Gera calendario de contas a pagar e alertas de vencimento.

Uso:
  python boleto_reader.py ler --arquivo boleto.pdf
  python boleto_reader.py ler --pasta ./boletos/
  python boleto_reader.py ler --mock
  python boleto_reader.py list
  python boleto_reader.py calendario
  python boleto_reader.py export --csv
  python boleto_reader.py export --json
  python boleto_reader.py export --html
  python boleto_reader.py pagar <id>
  python boleto_reader.py alertas
"""

# Author: Guilherme Crepaldi

import argparse
import glob
import os
import sys
import random
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.boleto_parser import parse_boleto, parse_texto_simulado
from parsers.codigo_barras import validar_codigo_barras
from db.database import conectar, inserir_boleto, listar_boletos, marcar_pago, remover_boleto, buscar_por_periodo
from helpers.calendario import gerar_calendario, exibir_calendario
from helpers.alerts import verificar_alertas, exibir_alertas, enviar_email_alerta
from helpers.export import exportar_csv, exportar_json, exportar_calendario_html
from config import DB_PATH

# ============================================================
# DADOS MOCK — simula leitura de boletos reais
# ============================================================

MOCK_BOLETOS = [
    {
        "texto": (
            "BOLETO BANCÁRIO\n"
            "Beneficiário: Enel Distribuição SP\n"
            "Valor: R$ 287,35\n"
            "Vencimento: 15/07/2026\n"
            "Linha Digitável: 23793.38128 60010.000000 01000.123456 7 8765400028735\n"
        ),
        "beneficiario": "Enel Distribuição SP",
        "valor": "287,35",
        "vencimento": "15/07/2026",
        "codigo_barras": "23793381286001000000001000123456787654000287358",
    },
    {
        "texto": (
            "BOLETO DE COBRANÇA\n"
            "Cedente: Sabesp S.A.\n"
            "Valor Total: R$ 189,50\n"
            "Data de Vencimento: 20/07/2026\n"
            "Código de Barras: 34191.23456 78901.234567 89012.345678 9 1234500018950\n"
        ),
        "beneficiario": "Sabesp S.A.",
        "valor": "189,50",
        "vencimento": "20/07/2026",
        "codigo_barras": "34191234567890123456789012345678912345000189503",
    },
    {
        "texto": (
            "FATURA\n"
            "Beneficiário: Vivo Telefonia\n"
            "Total: R$ 129,99\n"
            "Vencimento: 10/07/2026\n"
            "Código de Barras: 23790.12345 67890.123456 78901.234567 8 7654300012999\n"
        ),
        "beneficiario": "Vivo Telefonia",
        "valor": "129,99",
        "vencimento": "10/07/2026",
        "codigo_barras": "23790123456789012345678901234567876543000129998",
    },
    {
        "texto": (
            "CONTA DE CONDOMÍNIO\n"
            "Pagador: Condomínio Residencial Parque Verde\n"
            "Valor: R$ 890,00\n"
            "Vencimento: 25/07/2026\n"
        ),
        "beneficiario": "Condomínio Residencial Parque Verde",
        "valor": "890,00",
        "vencimento": "25/07/2026",
        "codigo_barras": None,
    },
    {
        "texto": (
            "BOLETO\n"
            "Favorecido: Academia FitPlus\n"
            "Valor: R$ 99,90\n"
            "Vencimento: 05/07/2026\n"
        ),
        "beneficiario": "Academia FitPlus",
        "valor": "99,90",
        "vencimento": "05/07/2026",
        "codigo_barras": None,
    },
]


def gerar_dados_mock():
    """Gera 3-5 boletos simulados para teste do modo --mock."""
    # Embaralha e pega uma quantidade aleatória
    selecao = random.sample(MOCK_BOLETOS, random.randint(3, 5))
    return selecao


# ============================================================
# COMANDOS
# ============================================================

def cmd_ler(args):
    """Comando 'ler': lê boletos de PDF(s) ou modo mock."""
    conn = conectar()
    boletos_lidos = []

    if args.mock:
        print("\n📄 MODO MOCK — Gerando dados simulados...\n")
        dados_mock = gerar_dados_mock()
        for dado in dados_mock:
            resultado = parse_texto_simulado(dado["texto"])
            # Se o parser não achou, usa os dados mock como fallback
            if not resultado["valor"]:
                resultado["valor"] = dado["valor"]
            if not resultado["vencimento"]:
                resultado["vencimento"] = dado["vencimento"]
            if not resultado["beneficiario"]:
                resultado["beneficiario"] = dado["beneficiario"]
            if not resultado["codigo_barras"]:
                resultado["codigo_barras"] = dado["codigo_barras"]

            exibir_boleto(resultado)
            boleto_id = inserir_boleto(conn, resultado)
            print(f"  ✅ Salvo no banco (ID: {boleto_id})\n")
            boletos_lidos.append(resultado)
        print(f"📊 Total: {len(boletos_lidos)} boleto(s) simulados importados.\n")
        conn.close()
        return

    if args.arquivo:
        caminhos = [args.arquivo]
    elif args.pasta:
        padrao = os.path.join(args.pasta, "*.pdf")
        caminhos = sorted(glob.glob(padrao))
        if not caminhos:
            print(f"  ⚠️  Nenhum PDF encontrado em: {args.pasta}")
            return
    else:
        print("  ❌ Use --arquivo <pdf>, --pasta <dir> ou --mock")
        return

    for caminho in caminhos:
        if not os.path.exists(caminho):
            print(f"  ⚠️  Arquivo não encontrado: {caminho}")
            continue
        print(f"\n📄 Lendo: {caminho}")
        try:
            resultado = parse_boleto(caminho)
            exibir_boleto(resultado)
            boleto_id = inserir_boleto(conn, resultado)
            print(f"  ✅ Salvo no banco (ID: {boleto_id})\n")
            boletos_lidos.append(resultado)
        except Exception as e:
            print(f"  ❌ Erro ao processar: {e}")

    print(f"📊 Total: {len(boletos_lidos)} boleto(s) importados.\n")
    conn.close()


def cmd_list(args):
    """Comando 'list': lista todos os boletos cadastrados."""
    conn = conectar()
    boletos = listar_boletos(conn, apenas_pendentes=args.pendentes)

    if not boletos:
        print("\n📭 Nenhum boleto cadastrado.\n")
        conn.close()
        return

    print(f"\n{'='*70}")
    print(f"  📋 LISTA DE BOLETOS ({len(boletos)})")
    print(f"{'='*70}\n")

    for b in boletos:
        pago = " ✅ PAGO" if b["pago"] else " ⏳ Pendente"
        print(f"  ID {b['id']:>3}: R$ {b.get('valor', '---'):>8} | "
              f"Venc: {b.get('vencimento', '---'):>10} | "
              f"{b.get('beneficiario', '?')[:30]:30s}{pago}")
    print(f"\n{'='*70}\n")
    conn.close()


def cmd_calendario(args):
    """Comando 'calendario': exibe calendário de contas a pagar."""
    conn = conectar()
    boletos = listar_boletos(conn, apenas_pendentes=True)
    calendario = gerar_calendario(boletos, dias=args.dias or 30)
    exibir_calendario(calendario)
    conn.close()


def cmd_export(args):
    """Comando 'export': exporta boletos para CSV, JSON ou HTML."""
    conn = conectar()
    boletos = listar_boletos(conn)

    if not boletos:
        print("\n📭 Nenhum boleto para exportar.\n")
        conn.close()
        return

    if args.csv:
        exportar_csv(boletos, args.csv if isinstance(args.csv, str) else "boletos_exportados.csv")
    if args.json:
        exportar_json(boletos, args.json if isinstance(args.json, str) else "boletos_exportados.json")
    if args.html:
        exportar_calendario_html(boletos, args.html if isinstance(args.html, str) else "calendario_contas.html")

    if not args.csv and not args.json and not args.html:
        # Padrão: exporta tudo
        exportar_csv(boletos)
        exportar_json(boletos)
        exportar_calendario_html(boletos)

    conn.close()


def cmd_pagar(args):
    """Comando 'pagar': marca um boleto como pago."""
    conn = conectar()
    try:
        marcar_pago(conn, args.id)
        print(f"  ✅ Boleto ID {args.id} marcado como pago.\n")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    conn.close()


def cmd_alertas(args):
    """Comando 'alertas': verifica vencimentos e exibe alertas."""
    conn = conectar()
    boletos = listar_boletos(conn, apenas_pendentes=True)
    if not boletos:
        print("\n📭 Nenhum boleto pendente.\n")
        conn.close()
        return

    resultados = verificar_alertas(boletos)
    exibir_alertas(resultados)

    if args.email:
        enviar_email_alerta(resultados, destinatario=args.email)

    conn.close()


def cmd_remover(args):
    """Comando 'remover': remove um boleto do banco."""
    conn = conectar()
    try:
        remover_boleto(conn, args.id)
        print(f"  ✅ Boleto ID {args.id} removido.\n")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    conn.close()


def cmd_validar(args):
    """Comando 'validar': valida um código de barras."""
    resultado = validar_codigo_barras(args.codigo)
    if resultado["valido"]:
        print(f"\n  ✅ {resultado['mensagem']}")
        print(f"  Código: {resultado['codigo_limpo']}\n")
    else:
        print(f"\n  ❌ {resultado['mensagem']}")
        if resultado["codigo_limpo"]:
            print(f"  Código: {resultado['codigo_limpo']}\n")


# ============================================================
# HELPERS
# ============================================================

def exibir_boleto(boleto: dict):
    """Exibe os dados de um boleto no console."""
    print(f"  ┌─────────────────────────────────────────────")
    print(f"  │ BENEFICIÁRIO:  {boleto.get('beneficiario', 'N/A')}")
    print(f"  │ VALOR:         R$ {boleto.get('valor', 'N/A')}")
    print(f"  │ VENCIMENTO:    {boleto.get('vencimento', 'N/A')}")
    cod = boleto.get("codigo_barras", "N/A")
    if cod and cod != "N/A":
        print(f"  │ CÓDIGO BARRAS: {cod}")
    else:
        print(f"  │ CÓDIGO BARRAS: Não encontrado")
    print(f"  └─────────────────────────────────────────────")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="📄 Boleto Reader — Leitor de boletos em PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s ler --mock                    # Modo simulado
  %(prog)s ler --arquivo boleto.pdf     # Ler um PDF específico
  %(prog)s ler --pasta ./boletos/       # Ler todos PDFs de uma pasta
  %(prog)s list                         # Listar boletos salvos
  %(prog)s list --pendentes             # Listar apenas pendentes
  %(prog)s calendario                   # Mostrar calendário 30 dias
  %(prog)s calendario --dias 60         # Mostrar calendário 60 dias
  %(prog)s export --csv                 # Exportar para CSV
  %(prog)s export --json                # Exportar para JSON
  %(prog)s export --html                # Exportar calendário HTML
  %(prog)s pagar 5                      # Marcar ID 5 como pago
  %(prog)s alertas                      # Verificar alertas
  %(prog)s alertas --email user@email.com
  %(prog)s validar 34191.23456...
  %(prog)s remover 3                    # Remover boleto ID 3
        """
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # ler
    p_ler = subparsers.add_parser("ler", help="Ler boletos de PDF(s)")
    p_ler.add_argument("--arquivo", "-a", type=str, help="Caminho do arquivo PDF")
    p_ler.add_argument("--pasta", "-p", type=str, help="Pasta com arquivos PDF")
    p_ler.add_argument("--mock", "-m", action="store_true", help="Usar dados simulados")

    # list
    p_list = subparsers.add_parser("list", help="Listar boletos cadastrados")
    p_list.add_argument("--pendentes", action="store_true", help="Apenas boletos não pagos")

    # calendario
    p_cal = subparsers.add_parser("calendario", help="Exibir calendário de contas")
    p_cal.add_argument("--dias", type=int, default=30, help="Número de dias (padrão: 30)")

    # export
    p_export = subparsers.add_parser("export", help="Exportar boletos")
    p_export.add_argument("--csv", nargs="?", const=True, help="Exportar para CSV (opcional: nome do arquivo)")
    p_export.add_argument("--json", nargs="?", const=True, help="Exportar para JSON (opcional: nome do arquivo)")
    p_export.add_argument("--html", nargs="?", const=True, help="Exportar calendário HTML (opcional: nome do arquivo)")

    # pagar
    p_pagar = subparsers.add_parser("pagar", help="Marcar boleto como pago")
    p_pagar.add_argument("id", type=int, help="ID do boleto")

    # alertas
    p_alertas = subparsers.add_parser("alertas", help="Verificar alertas de vencimento")
    p_alertas.add_argument("--email", type=str, help="Enviar alerta por email (opcional)")

    # validar
    p_validar = subparsers.add_parser("validar", help="Validar código de barras")
    p_validar.add_argument("codigo", type=str, help="Código de barras para validar")

    # remover
    p_remover = subparsers.add_parser("remover", help="Remover boleto do banco")
    p_remover.add_argument("id", type=int, help="ID do boleto")

    args = parser.parse_args()

    if args.comando == "ler":
        cmd_ler(args)
    elif args.comando == "list":
        cmd_list(args)
    elif args.comando == "calendario":
        cmd_calendario(args)
    elif args.comando == "export":
        cmd_export(args)
    elif args.comando == "pagar":
        cmd_pagar(args)
    elif args.comando == "alertas":
        cmd_alertas(args)
    elif args.comando == "validar":
        cmd_validar(args)
    elif args.comando == "remover":
        cmd_remover(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
