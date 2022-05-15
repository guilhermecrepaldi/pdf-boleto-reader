"""
Validação de código de barras com dígito verificador (módulo 10 ou 11).
TODO: implementar validacao para todos os bancos
"""

# Author: Guilherme Crepaldi

import re


def digito_verificador_mod10(numero: str) -> int:
    """
    Calcula o dígito verificador módulo 10.
    Multiplica cada dígito por 2, 1, 2, 1... da direita pra esquerda,
    soma os dígitos dos resultados, complemento para múltiplo de 10.
    """
    soma = 0
    multiplicador = 2
    for digito in reversed(numero):
        resultado = int(digito) * multiplicador
        soma += resultado // 10 + resultado % 10
        multiplicador = 3 - multiplicador  # alterna entre 2 e 1
    resto = soma % 10
    return (10 - resto) if resto != 0 else 0


def digito_verificador_mod11(numero: str) -> int:
    """
    Calcula o dígito verificador módulo 11.
    Multiplica cada dígito por 2, 3, 4, 5, 6, 7, 2, 3... da direita pra esquerda,
    soma, resto por 11.
    """
    pesos = [2, 3, 4, 5, 6, 7]
    soma = 0
    for i, digito in enumerate(reversed(numero)):
        peso = pesos[i % len(pesos)]
        soma += int(digito) * peso
    resto = soma % 11
    if resto == 0 or resto == 1:
        return 0
    return 11 - resto


def validar_codigo_barras(codigo: str) -> dict:
    """
    Valida um código de barras de boleto bancário.
    - Remove caracteres não numéricos
    - Verifica se tem 44 ou 47 dígitos
    - Valida o(s) dígito(s) verificador(es)

    Retorna dict com:
      - valido: bool
      - mensagem: str explicativa
      - codigo_limpo: str só com dígitos
    """
    if not codigo:
        return {"valido": False, "mensagem": "Código vazio.", "codigo_limpo": ""}

    codigo_limpo = re.sub(r"[^\d]", "", codigo)

    if len(codigo_limpo) not in (44, 47):
        return {
            "valido": False,
            "mensagem": f"Código com {len(codigo_limpo)} dígitos (esperado 44 ou 47).",
            "codigo_limpo": codigo_limpo,
        }

    # Para código de 47 dígitos (boleto com digito verificador por campo)
    if len(codigo_limpo) == 47:
        # Blocos: campo1 (9 dígitos + 1 DV), campo2 (10 dígitos + 1 DV),
        # campo3 (10 dígitos + 1 DV), campo4 (5 dígitos), campo5 (10 dígitos + 1 DV)
        # Na prática, cada campo tem seu próprio DV
        erros = []
        campos = [
            (codigo_limpo[0:9], codigo_limpo[9], "Campo 1"),
            (codigo_limpo[10:20], codigo_limpo[20], "Campo 2"),
            (codigo_limpo[21:31], codigo_limpo[31], "Campo 3"),
            (codigo_limpo[32:42], codigo_limpo[42], "Campo 5"),
        ]
        for digitos, dv_esperado, nome in campos:
            dv_calculado = digito_verificador_mod10(digitos)
            if dv_calculado != int(dv_esperado):
                erros.append(f"{nome}: DV esperado {dv_esperado}, calculado {dv_calculado}")

        if erros:
            return {
                "valido": False,
                "mensagem": "; ".join(erros),
                "codigo_limpo": codigo_limpo,
            }
        return {
            "valido": True,
            "mensagem": "Código de barras válido (47 dígitos).",
            "codigo_limpo": codigo_limpo,
        }

    # Para código de 44 dígitos (código de barras simplificado)
    # DV geral: posição 4 (0-indexed: 3)
    if len(codigo_limpo) == 44:
        # O dígito verificador geral está na 5ª posição (índice 4)
        dv_esperado = int(codigo_limpo[4])
        codigo_sem_dv = codigo_limpo[:4] + codigo_limpo[5:]
        dv_calculado = digito_verificador_mod11(codigo_sem_dv)

        if dv_calculado == dv_esperado:
            return {
                "valido": True,
                "mensagem": "Código de barras válido (44 dígitos).",
                "codigo_limpo": codigo_limpo,
            }
        return {
            "valido": False,
            "mensagem": f"DV geral: esperado {dv_esperado}, calculado {dv_calculado}.",
            "codigo_limpo": codigo_limpo,
        }

    return {"valido": False, "mensagem": "Formato não reconhecido.", "codigo_limpo": codigo_limpo}
