# 📄 PDF Boleto Reader

**Extract, organize, and track Brazilian bank slip (boleto) data from PDF files.**

A command-line tool that parses PDF boletos to extract payment information (value, due date, barcode, payee), stores a searchable history in SQLite, generates a payment calendar with visual alerts, and exports to CSV/JSON/HTML.

## Features

- **PDF Parsing** — Extract text from boletos using `pdfplumber` with regex patterns for Brazilian boleto formats
- **Barcode Validation** — Validate 44- and 47-digit barcodes with modulo 10/11 check digits
- **SQLite History** — Persistent storage with payment tracking (paid/pending)
- **Payment Calendar** — Organize bills by due date with 30/60-day views
- **Alert System** — Color-coded urgency (🔴 overdue, 🟡 due within 5 days, 🟢 on schedule) + optional email notification
- **Export** — CSV, JSON, and interactive HTML calendar report
- **Mock Mode** — Generate simulated boleto data for testing without real PDFs

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd pdf-boleto-reader

# Install dependencies
pip install -r requirements.txt
```

Requires **Python 3.10+** and `pdfplumber`.

## Usage

### Read a boleto PDF

```bash
python boleto_reader.py ler --arquivo caminho/do/boleto.pdf
python boleto_reader.py ler --pasta ./boletos/        # Batch process a folder
```

### Test without real PDFs

```bash
python boleto_reader.py ler --mock
```

Generates 3–5 simulated boletos (Enel, Sabesp, Vivo, etc.) so you can explore all commands without actual PDF files.

### List stored boletos

```bash
python boleto_reader.py list                # All
python boleto_reader.py list --pendentes    # Unpaid only
```

### Payment calendar

```bash
python boleto_reader.py calendario                    # Next 30 days
python boleto_reader.py calendario --dias 60          # Next 60 days
```

### Alerts

```bash
python boleto_reader.py alertas                       # Console alerts
python boleto_reader.py alertas --email user@ex.com   # Email notification
```

### Export

```bash
python boleto_reader.py export              # CSV + JSON + HTML
python boleto_reader.py export --csv        # CSV only
python boleto_reader.py export --json       # JSON only
python boleto_reader.py export --html       # HTML calendar
python boleto_reader.py export --csv relatorio.csv   # Custom filename
```

### Manage

```bash
python boleto_reader.py pagar 5            # Mark ID 5 as paid
python boleto_reader.py remover 3          # Delete ID 3
python boleto_reader.py validar 34191.23456...  # Validate a barcode
```

## Project Structure

```
pdf-boleto-reader/
├── boleto_reader.py          # CLI entry point
├── config.py                 # Settings & regex patterns
├── parsers/
│   ├── boleto_parser.py      # PDF text extraction & regex parsing
│   └── codigo_barras.py      # Barcode validation (mod 10/11)
├── db/
│   └── database.py           # SQLite CRUD operations
├── helpers/
│   ├── calendario.py         # Payment calendar generation
│   ├── alerts.py             # Due-date alerts (console + email)
│   └── export.py             # CSV/JSON/HTML exporters
├── samples/
│   └── README.md             # Sample PDF instructions
├── requirements.txt
├── .gitignore
└── README.md
```

## How It Works

1. **PDF Parsing** (`parsers/boleto_parser.py`): Opens each PDF with `pdfplumber`, extracts all text, then applies regex patterns to find value (`R$ 1.234,56`), due date (`dd/mm/yyyy`), barcode (47 digits), and payee name. The parser tries multiple patterns because each bank has a slightly different layout.

2. **Barcode Validation** (`parsers/codigo_barras.py`): Validates check digits using modulo 10 (per-field for 47-digit codes) and modulo 11 (general DV for 44-digit codes).

3. **Storage** (`db/database.py`): Each parsed boleto is stored in `db/boletos.db` with fields: `id`, `arquivo`, `valor`, `vencimento`, `codigo_barras`, `beneficiario`, `lido_em`, `pago`.

4. **Calendar & Alerts** (`utils/`): Organizes by due date, compares against today, and produces color-coded urgency output.

## Configuration

Edit `config.py` to:
- Adjust regex patterns for different boleto layouts
- Change alert thresholds (`ALERTA_DIAS_AMARELO`)
- Set up SMTP email alerts (or use env vars: `BOLETO_SMTP_SERVER`, `BOLETO_EMAIL_TO`, etc.)

## Limitations

- Parsing relies on regex patterns that cover most (but not all) brazilian bank boleto layouts
- Barcode validation is implemented for common formats; some banks use proprietary DV algorithms (see `# TODO` in `codigo_barras.py`)
- Requires Python 3.10+ for `str | None` type hints

## License

MIT — feel free to use, modify, and share.

## Author

**Guilherme Crepaldi**
