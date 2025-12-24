# Bingo Ticket Generator

Python script to generate British-style bingo tickets with QR codes for the Bingo Game Manager app.

## Features

- Generates valid British bingo cards (9x3 grid, 5 numbers per row, 4 blanks per row)
- Creates QR codes with binary ticket data
- Outputs PDF with 3 tickets per A4 page
- Front side shows numbered tickets, back side shows QR codes
- Generates CSV with all ticket data

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install reportlab qrcode[pil] pillow
```

## Usage

Generate 30 tickets (default):

```bash
python generate_tickets.py
```

Generate a specific number of tickets:

```bash
python generate_tickets.py -n 60
```

Specify output filenames:

```bash
python generate_tickets.py -n 100 -o my_tickets.pdf -c my_tickets.csv
```

## Options

- `-n, --num-tickets`: Number of tickets to generate (default: 30)
- `-o, --output`: Output PDF filename (default: bingo_tickets.pdf)
- `-c, --csv`: Output CSV filename (default: bingo_tickets.csv)
- `-h, --help`: Show help message

## QR Code Format

Each QR code contains binary data in the following format:
- **Bytes 0-1**: Ticket ID (16-bit unsigned integer, little endian)
- **Bytes 2-28**: Card contents (27 bytes, one per cell, left-to-right, top-to-bottom)
  - Value 0 = blank cell
  - Values 1-90 = number in that cell

QR code specifications:
- Version: 4
- Error correction: M (Medium, ~15% recovery)

## PDF Layout

- **Page size**: A4
- **Tickets per page**: 3 (vertical layout)
- **Pages**: Alternating front and back
  - Odd pages: Front side with numbers
  - Even pages: Back side with QR codes (reversed order for duplex printing)

## CSV Format

The CSV file contains one row per ticket with columns:
- `id`: Ticket ID (sequential, starting from 1)
- `cell_0` to `cell_26`: Contents of each cell (0 = blank, 1-90 = number)

Cells are ordered left-to-right, top-to-bottom.

## British Bingo Card Rules

Valid British bingo cards follow these rules:
- 9 columns × 3 rows (27 total cells)
- Each row has exactly 5 numbers and 4 blanks
- Column 1: numbers 1-9
- Column 2: numbers 10-19
- Column 3: numbers 20-29
- Column 4: numbers 30-39
- Column 5: numbers 40-49
- Column 6: numbers 50-59
- Column 7: numbers 60-69
- Column 8: numbers 70-79
- Column 9: numbers 80-90
- Numbers in each column are sorted top to bottom
