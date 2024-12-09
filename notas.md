# Anotações do Projeto — PDF Boleto Reader

## Como usar no dia a dia

```bash
# 1. Ler boletos da pasta
python boleto_reader.py ler --pasta C:/Users/Home/Downloads/boletos/

# 2. Ver calendário
python boleto_reader.py calendario

# 3. Ver alertas
python boleto_reader.py alertas

# 4. Pagar um boleto
python boleto_reader.py pagar 1

# 5. Exportar relatório
python boleto_reader.py export --html
```

## Modo mock pra apresentar

```bash
python boleto_reader.py ler --mock
python boleto_reader.py list
python boleto_reader.py calendario
python boleto_reader.py alertas
python boleto_reader.py export --html
```

## Ideias futuras

- Interface web com Flask/FastAPI
- OCR para boletos scaneados (pdfplumber só pega texto嵌入)
- Categorização automática (água, luz, aluguel, etc.)
- Importação de XML/NFe
- Dashboard com gráficos de gastos mensais
- Integração com WhatsApp (alerta via Twilio/WhatsApp API)

## Bancos testados

- [ ] Itaú
- [ ] Bradesco
- [ ] Santander
- [ ] Caixa
- [ ] Banco do Brasil
- [ ] Sicredi
- [ ] Enel (funciona)
- [ ] Sabesp (funciona)

## Observações

- O pdfplumber não lê PDF escaneado (imagem) — só PDF com texto nativo
- Cada banco tem um layout diferente. Os padrões regex cobrem os mais comuns
- O --mock é essencial pra testar sem ter que ficar baixando boleto real

## Author

**Guilherme Crepaldi**
