#!/usr/bin/env python3
"""
British Bingo Card Generator

Generates British-style bingo tickets with QR codes for the Bingo Game Manager app.
Each ticket has 9 columns x 3 rows with 5 numbers per row and 4 blanks per row.
"""

import random
import csv
import struct
from typing import List, Tuple
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    import qrcode
    from io import BytesIO
    from PIL import Image
except ImportError as e:
    print("Error: Missing required libraries.")
    print("Please install: pip install reportlab qrcode[pil] pillow")
    raise e


class BritishBingoCard:
    """Generates a British-style bingo card (9x3 grid, 5 numbers per row)"""

    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(3)]

    def generate(self) -> List[List[int]]:
        """Generate a valid British bingo card"""
        # Column ranges for British bingo
        column_ranges = [
            (1, 9),    # Column 0: 1-9
            (10, 19),  # Column 1: 10-19
            (20, 29),  # Column 2: 20-29
            (30, 39),  # Column 3: 30-39
            (40, 49),  # Column 4: 40-49
            (50, 59),  # Column 5: 50-59
            (60, 69),  # Column 6: 60-69
            (70, 79),  # Column 7: 70-79
            (80, 90),  # Column 8: 80-90
        ]

        # Generate numbers for each column
        for col in range(9):
            min_val, max_val = column_ranges[col]
            available_numbers = list(range(min_val, max_val + 1))
            random.shuffle(available_numbers)

            # Each column gets 1-3 numbers distributed across rows
            # We'll use a simple distribution: try to get close to 15 total numbers
            # with 5 per row
            num_in_column = min(3, len(available_numbers))

            # Select which rows get numbers in this column
            rows_to_fill = random.sample(range(3), num_in_column)

            for i, row in enumerate(rows_to_fill):
                self.grid[row][col] = available_numbers[i]

        # Ensure each row has exactly 5 numbers and 4 blanks
        self._balance_rows()

        # Sort numbers in each column (top to bottom)
        self._sort_columns()

        return self.grid

    def _balance_rows(self):
        """Ensure each row has exactly 5 numbers and 4 blanks"""
        for row_idx in range(3):
            row = self.grid[row_idx]
            num_count = sum(1 for cell in row if cell != 0)

            if num_count < 5:
                # Need to add numbers
                empty_cols = [i for i, cell in enumerate(row) if cell == 0]
                cols_to_fill = random.sample(empty_cols, 5 - num_count)

                for col in cols_to_fill:
                    # Get a number from this column's range
                    min_val, max_val = self._get_column_range(col)
                    # Find a number not already used in this column
                    used_in_col = [self.grid[r][col] for r in range(3)]
                    available = [n for n in range(min_val, max_val + 1) if n not in used_in_col]
                    if available:
                        self.grid[row_idx][col] = random.choice(available)

            elif num_count > 5:
                # Need to remove numbers
                filled_cols = [i for i, cell in enumerate(row) if cell != 0]
                cols_to_empty = random.sample(filled_cols, num_count - 5)

                for col in cols_to_empty:
                    self.grid[row_idx][col] = 0

    def _sort_columns(self):
        """Sort numbers in each column from top to bottom"""
        for col in range(9):
            column_values = [self.grid[row][col] for row in range(3) if self.grid[row][col] != 0]
            column_values.sort()

            value_idx = 0
            for row in range(3):
                if self.grid[row][col] != 0:
                    self.grid[row][col] = column_values[value_idx]
                    value_idx += 1

    def _get_column_range(self, col: int) -> Tuple[int, int]:
        """Get the valid number range for a column"""
        ranges = [
            (1, 9), (10, 19), (20, 29), (30, 39), (40, 49),
            (50, 59), (60, 69), (70, 79), (80, 90)
        ]
        return ranges[col]

    def to_flat_list(self) -> List[int]:
        """Convert grid to flat list (left to right, top to bottom)"""
        result = []
        for row in self.grid:
            result.extend(row)
        return result


def generate_qr_code(ticket_id: int, card_data: List[int]) -> Image:
    """
    Generate QR code for a ticket

    Format:
    - First 2 bytes: ticket ID (little endian)
    - Next 27 bytes: card contents (0 = blank)
    """
    # Pack ticket ID as 2-byte little endian
    binary_data = struct.pack('<H', ticket_id)

    # Add card data (27 bytes)
    for value in card_data:
        binary_data += struct.pack('B', value)

    # Generate QR code (Version 4, Error correction M)
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    qr.add_data(binary_data, optimize=0)
    qr.make(fit=False)

    img = qr.make_image(fill_color="black", back_color="white")
    return img


def draw_ticket_front(c: canvas.Canvas, card_data: List[int], x: float, y: float,
                     ticket_id: int, cell_width: float = 10*mm, cell_height: float = 12*mm):
    """Draw a bingo ticket on the PDF (front side with numbers)"""
    # Title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y + cell_height * 3 + 5*mm, f"Ticket #{ticket_id}")

    # Draw grid
    c.setFont("Helvetica-Bold", 14)
    for row in range(3):
        for col in range(9):
            cell_x = x + col * cell_width
            cell_y = y + (2 - row) * cell_height

            # Draw cell border
            c.rect(cell_x, cell_y, cell_width, cell_height)

            # Draw number if not blank
            idx = row * 9 + col
            if card_data[idx] != 0:
                # Center the number in the cell
                num_str = str(card_data[idx])
                text_width = c.stringWidth(num_str, "Helvetica-Bold", 14)
                text_x = cell_x + (cell_width - text_width) / 2
                text_y = cell_y + (cell_height - 5*mm) / 2
                c.drawString(text_x, text_y, num_str)


def draw_ticket_back(c: canvas.Canvas, ticket_id: int, card_data: List[int],
                    x: float, y: float, qr_size: float = 30*mm):
    """Draw the back of a ticket with QR code"""
    # Generate QR code
    qr_img = generate_qr_code(ticket_id, card_data)

    # Save QR code to bytes
    img_buffer = BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # Center QR code in ticket area
    qr_x = x + (90*mm - qr_size) / 2
    qr_y = y + (36*mm - qr_size) / 2 + 5*mm

    # Draw QR code
    c.drawImage(img_buffer, qr_x, qr_y, width=qr_size, height=qr_size)

    # Add ticket ID below QR code
    c.setFont("Helvetica", 8)
    text = f"Ticket #{ticket_id}"
    text_width = c.stringWidth(text, "Helvetica", 8)
    c.drawString(x + (90*mm - text_width) / 2, qr_y - 5*mm, text)


def generate_tickets_pdf(num_tickets: int, output_pdf: str = "bingo_tickets.pdf",
                        output_csv: str = "bingo_tickets.csv"):
    """
    Generate bingo tickets PDF and CSV

    Args:
        num_tickets: Number of tickets to generate
        output_pdf: Output PDF filename
        output_csv: Output CSV filename
    """
    # Generate all tickets
    tickets = []
    for ticket_id in range(1, num_tickets + 1):
        card = BritishBingoCard()
        card.generate()
        card_data = card.to_flat_list()
        tickets.append((ticket_id, card_data))

    # Create PDF
    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_width, page_height = A4

    # Calculate positions for 3 tickets per page
    ticket_width = 90 * mm
    ticket_height = 50 * mm
    margin_left = (page_width - ticket_width) / 2

    # Positions for 3 tickets vertically on a page
    y_positions = [
        page_height - 70*mm,   # Top ticket
        page_height - 140*mm,  # Middle ticket
        page_height - 210*mm,  # Bottom ticket
    ]

    # Generate pages
    for page_start in range(0, num_tickets, 3):
        tickets_on_page = tickets[page_start:page_start + 3]

        # Draw front side
        for idx, (ticket_id, card_data) in enumerate(tickets_on_page):
            draw_ticket_front(c, card_data, margin_left, y_positions[idx], ticket_id)

        c.showPage()

        # Draw back side (reversed order for proper alignment when printed duplex)
        for idx, (ticket_id, card_data) in enumerate(reversed(tickets_on_page)):
            draw_ticket_back(c, ticket_id, card_data, margin_left, y_positions[idx])

        c.showPage()

    c.save()
    print(f"Generated PDF: {output_pdf}")

    # Create CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Header
        header = ['id'] + [f'cell_{i}' for i in range(27)]
        writer.writerow(header)

        # Data
        for ticket_id, card_data in tickets:
            row = [ticket_id] + card_data
            writer.writerow(row)

    print(f"Generated CSV: {output_csv}")
    print(f"Total tickets generated: {num_tickets}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate British Bingo tickets with QR codes")
    parser.add_argument('-n', '--num-tickets', type=int, default=30,
                       help='Number of tickets to generate (default: 30)')
    parser.add_argument('-o', '--output', type=str, default='bingo_tickets.pdf',
                       help='Output PDF filename (default: bingo_tickets.pdf)')
    parser.add_argument('-c', '--csv', type=str, default='bingo_tickets.csv',
                       help='Output CSV filename (default: bingo_tickets.csv)')

    args = parser.parse_args()

    generate_tickets_pdf(args.num_tickets, args.output, args.csv)
