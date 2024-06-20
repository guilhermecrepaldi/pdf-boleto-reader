# Boletos de Exemplo (Sample PDFs)

Este diretório é para armazenar boletos em PDF reais para teste.

## Como testar

1. Coloque arquivos `.pdf` de boletos reais (seus) neste diretório
2. Execute:

```bash
python boleto_reader.py ler --pasta samples/
```

## Modo Mock (recomendado para testes)

Se você não tem boletos em PDF disponíveis, use o modo `--mock` que gera dados simulados:

```bash
python boleto_reader.py ler --mock
```

Isso criará de 3 a 5 boletos fictícios (Enel, Sabesp, Vivo, etc.) no banco de dados para que você possa testar todos os comandos sem depender de PDFs reais.

## Requisitos

Para ler PDFs reais, é necessário ter o `pdfplumber` instalado:

```bash
pip install pdfplumber
```

## Observação

Não incluímos PDFs de exemplo porque boletos bancários contêm dados
pessoais e códigos de barras válidos. Use seus próprios boletos ou
o modo `--mock` para testes.
