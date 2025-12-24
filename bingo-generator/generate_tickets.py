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
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import qrcode
    from io import BytesIO
    from PIL import Image
except ImportError as e:
    print("Error: Missing required libraries.")
    print("Please install: pip install reportlab qrcode[pil] pillow")
    raise e


# Numbers to exclude from generated tickets (missing from physical set)
EXCLUDED_NUMBERS = [20, 72]


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
            available_numbers = [n for n in range(min_val, max_val + 1) if n not in EXCLUDED_NUMBERS]
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
                    available = [n for n in range(min_val, max_val + 1)
                                if n not in used_in_col and n not in EXCLUDED_NUMBERS]
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
                     ticket_id: int, scale: float = 1.0):
    """Draw a bingo ticket on the PDF (front side with numbers)"""
    # Calculate dimensions based on scale
    cell_width = 10 * mm * scale
    cell_height = 12 * mm * scale
    font_size = 14 * scale
    id_font_size = 8 * scale

    # Draw grid
    c.setFont("Helvetica-Bold", font_size)
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
                text_width = c.stringWidth(num_str, "Helvetica-Bold", font_size)
                text_x = cell_x + (cell_width - text_width) / 2
                text_y = cell_y + (cell_height - 5*mm*scale) / 2
                c.drawString(text_x, text_y, num_str)

    # Draw 4-digit ticket ID on bottom left
    c.setFont("Helvetica", id_font_size)
    id_str = f"{ticket_id:04d}"
    c.drawString(x, y - 4*mm*scale, id_str)


def draw_ticket_back(c: canvas.Canvas, ticket_id: int, card_data: List[int],
                    x: float, y: float, scale: float = 1.0):
    """Draw the back of a ticket with QR code centered in the same space as front ticket"""
    # Calculate dimensions based on scale
    qr_size = 30 * mm * scale
    ticket_width = 90 * mm * scale
    ticket_height = 36 * mm * scale  # Same height as front ticket grid
    id_font_size = 8 * scale

    # Generate QR code
    qr_img = generate_qr_code(ticket_id, card_data)

    # Save QR code to bytes
    img_buffer = BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # Center QR code horizontally and vertically in ticket area
    qr_x = x + (ticket_width - qr_size) / 2
    qr_y = y + (ticket_height - qr_size) / 2

    # Draw QR code using ImageReader
    c.drawImage(ImageReader(img_buffer), qr_x, qr_y, width=qr_size, height=qr_size)

    # Add 4-digit ticket ID below QR code
    c.setFont("Helvetica", id_font_size)
    id_str = f"{ticket_id:04d}"
    text_width = c.stringWidth(id_str, "Helvetica", id_font_size)
    c.drawString(x + (ticket_width - text_width) / 2, qr_y - 4*mm*scale, id_str)


def generate_tickets_pdf(num_tickets: int, output_pdf: str = "bingo_tickets.pdf",
                        output_csv: str = "bingo_tickets.csv", scale: float = 1.0,
                        title: str = None, title_font: str = "Christmas Merryland"):
    """
    Generate bingo tickets PDF and CSV

    Args:
        num_tickets: Number of tickets to generate
        output_pdf: Output PDF filename
        output_csv: Output CSV filename
        scale: Scale factor for ticket size and fonts (1.0 to 2.0)
        title: Optional title to display at top of front pages
        title_font: Font name for the title (default: Christmas Merryland)
    """
    # Generate random unique 4-digit ticket IDs
    all_ids = list(range(1000, 10000))
    random.shuffle(all_ids)
    ticket_ids = all_ids[:num_tickets]

    # Generate all tickets
    tickets = []
    for ticket_id in ticket_ids:
        card = BritishBingoCard()
        card.generate()
        card_data = card.to_flat_list()
        tickets.append((ticket_id, card_data))

    # Register custom fonts
    script_dir = Path(__file__).parent
    christmas_font_path = script_dir / "ChristmasMerryland.ttf"
    if christmas_font_path.exists():
        pdfmetrics.registerFont(TTFont('Christmas Merryland', str(christmas_font_path)))

    # Create PDF
    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_width, page_height = A4

    # ===== STANDARD PAGE LAYOUT =====
    # Page height: 297mm (A4)
    # Title position: 20mm from top (page_height - 20mm) if title exists
    # Content starts: 40mm from top (leaving space for title)
    #
    # Dashed cutting lines:
    #   Line 1: 125mm from top (page_height - 125mm)
    #   Line 2: 210mm from top (page_height - 210mm)
    #
    # Ticket center positions (middle of each section):
    #   Top section (40-125mm, 85mm tall): center at 82.5mm from top
    #   Middle section (125-210mm, 85mm tall): center at 167.5mm from top
    #   Bottom section (210-297mm, 87mm tall): center at 253.5mm from top
    # ================================

    # Fixed positions for cutting lines (constant regardless of scale)
    cut_line_positions = [
        page_height - 125 * mm,  # First cutting line
        page_height - 210 * mm,  # Second cutting line
    ]

    # Fixed positions for ticket centers (where tickets should be vertically centered)
    ticket_center_positions = [
        page_height - 82.5 * mm,   # Top ticket center
        page_height - 167.5 * mm,  # Middle ticket center
        page_height - 253.5 * mm,  # Bottom ticket center
    ]

    # Title position
    title_y_position = page_height - 20 * mm

    # Calculate ticket dimensions
    ticket_width = 90 * mm * scale
    ticket_content_height = 36 * mm * scale  # Height of the actual bingo grid
    margin_left = (page_width - ticket_width) / 2

    # Generate pages
    for page_start in range(0, num_tickets, 3):
        tickets_on_page = tickets[page_start:page_start + 3]

        # Draw front side
        if title:
            # Draw title at top of page
            try:
                c.setFont(title_font, 18)
            except KeyError:
                # Fallback to Helvetica if font not found
                c.setFont('Helvetica-Bold', 18)
            title_width = c.stringWidth(title, title_font if title_font in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 18)
            c.drawString((page_width - title_width) / 2, title_y_position, title)

        # Draw cutting lines (dashed)
        c.setDash(3, 3)
        for cut_y in cut_line_positions:
            c.line(20*mm, cut_y, page_width - 20*mm, cut_y)
        c.setDash()  # Reset to solid line

        for idx, (ticket_id, card_data) in enumerate(tickets_on_page):
            # Calculate y position so ticket is centered at ticket_center_positions[idx]
            # The draw function expects the bottom y coordinate of the ticket
            ticket_y = ticket_center_positions[idx] - (ticket_content_height / 2)
            draw_ticket_front(c, card_data, margin_left, ticket_y, ticket_id, scale)

        c.showPage()

        # Draw back side (reversed order for proper alignment when printed duplex)
        # Draw cutting lines (dashed)
        c.setDash(3, 3)
        for cut_y in cut_line_positions:
            c.line(20*mm, cut_y, page_width - 20*mm, cut_y)
        c.setDash()  # Reset to solid line

        for idx, (ticket_id, card_data) in enumerate(reversed(tickets_on_page)):
            # Use same center positions (reversed order for duplex printing)
            reverse_idx = len(tickets_on_page) - 1 - idx
            ticket_y = ticket_center_positions[reverse_idx] - (ticket_content_height / 2)
            draw_ticket_back(c, ticket_id, card_data, margin_left, ticket_y, scale)

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
    parser.add_argument('-s', '--scale', type=float, default=1.0,
                       help='Scale factor for ticket size and fonts, 1.0 to 2.0 (default: 1.0)')
    parser.add_argument('-t', '--title', type=str, default=None,
                       help='Title to display at top of front pages (default: none)')
    parser.add_argument('-f', '--title-font', type=str, default='Christmas Merryland',
                       help='Font name for the title (default: Christmas Merryland)')

    args = parser.parse_args()

    # Validate scale
    if args.scale < 1.0 or args.scale > 2.0:
        parser.error("Scale must be between 1.0 and 2.0")

    generate_tickets_pdf(args.num_tickets, args.output, args.csv, args.scale,
                        args.title, args.title_font)
