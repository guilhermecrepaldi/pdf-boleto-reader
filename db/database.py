"""
SQLite para histórico de boletos lidos.
"""

# Author: Guilherme Crepaldi

import sqlite3
import os
from datetime import datetime


def get_db_path():
    """Retorna o caminho do banco de dados SQLite."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "boletos.db")


def conectar():
    """Conecta ao banco SQLite e cria tabela se não existir."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    criar_tabela(conn)
    return conn


def criar_tabela(conn):
    """Cria a tabela 'boletos' se não existir."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS boletos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo TEXT NOT NULL,
            valor TEXT,
            vencimento TEXT,
            codigo_barras TEXT,
            beneficiario TEXT,
            lido_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            pago INTEGER DEFAULT 0
        )
    """)
    conn.commit()


def inserir_boleto(conn, boleto: dict) -> int:
    """
    Insere um boleto no banco.
    Retorna o ID inserido.
    """
    cursor = conn.execute("""
        INSERT INTO boletos (arquivo, valor, vencimento, codigo_barras, beneficiario)
        VALUES (?, ?, ?, ?, ?)
    """, (
        boleto.get("arquivo", ""),
        boleto.get("valor"),
        boleto.get("vencimento"),
        boleto.get("codigo_barras"),
        boleto.get("beneficiario"),
    ))
    conn.commit()
    return cursor.lastrowid


def listar_boletos(conn, apenas_pendentes: bool = False) -> list:
    """
    Lista todos os boletos cadastrados.
    Se apenas_pendentes=True, filtra só os não pagos.
    """
    if apenas_pendentes:
        cursor = conn.execute(
            "SELECT * FROM boletos WHERE pago = 0 ORDER BY vencimento ASC"
        )
    else:
        cursor = conn.execute("SELECT * FROM boletos ORDER BY lido_em DESC")
    return [dict(row) for row in cursor.fetchall()]


def marcar_pago(conn, boleto_id: int):
    """Marca um boleto como pago."""
    conn.execute("UPDATE boletos SET pago = 1 WHERE id = ?", (boleto_id,))
    conn.commit()


def remover_boleto(conn, boleto_id: int):
    """Remove um boleto do banco."""
    conn.execute("DELETE FROM boletos WHERE id = ?", (boleto_id,))
    conn.commit()


def buscar_por_periodo(conn, dias: int = 30) -> list:
    """
    Busca boletos com vencimento nos próximos N dias.
    """
    cursor = conn.execute("""
        SELECT * FROM boletos
        WHERE vencimento IS NOT NULL AND vencimento != ''
        ORDER BY vencimento ASC
    """)
    todos = [dict(row) for row in cursor.fetchall()]
    from datetime import datetime, timedelta
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    limite = hoje + timedelta(days=dias)

    resultado = []
    for b in todos:
        try:
            data_venc = datetime.strptime(b["vencimento"], "%d/%m/%Y")
            if hoje <= data_venc <= limite:
                resultado.append(b)
        except ValueError:
            continue
    return resultado
