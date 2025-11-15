"""
PDFWriter Module

This module provides functionality to generate a PDF document for a car, 
including car details (title, mileage, configuration) and images.

It defines:

- PDFWriter: A class for creating PDF files with an internal cursor
- create_pdf: A high-level function to generate a PDF from a JSON file containing
  car data and associated images.
"""

import json
import os
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import simpleSplit
from PIL import Image


DEFAULT_MARGIN = 50
DEFAULT_FONT_SIZE = 12
DEFAULT_LINE_SPACING = 15
DEFAULT_IMAGE_SPACING = 10
DEFAULT_FONT_NAME = "NotoSans"
DEFAULT_FONT_PATH = "NotoSans.ttf"
DEFAULT_PAGE_SIZE = A4


class PDFWriter:
    """Compact PDF writer with internal cursor."""

    def __init__(self, output_pdf: str, page_size=DEFAULT_PAGE_SIZE,
                 margin=DEFAULT_MARGIN):
        self.output_pdf = output_pdf
        self.width, self.height = page_size
        self.margin = margin
        self.y_cursor = self.height - margin
        self.c = canvas.Canvas(output_pdf, pagesize=page_size)
        self.font_name = DEFAULT_FONT_NAME

    def register_font(self, font_name=DEFAULT_FONT_NAME, font_path=DEFAULT_FONT_PATH):
        """Register a TrueType font for use in the PDF."""
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        self.c.setFont(self.font_name, DEFAULT_FONT_SIZE)
        self.font_name = font_name

    def draw_car_info(self, car_data, font_size=DEFAULT_FONT_SIZE,
                      line_spacing=DEFAULT_LINE_SPACING):
        """Draw car title, mileage, and configuration information."""
        self._draw_text_block(car_data.get("title", "No Title"),
                              font_size, line_spacing)
        mileage = car_data.get("mileage", 0)
        self._draw_text_block(f"Пробег: {int(mileage*10000)} км",
                              font_size, line_spacing)
        for k, v in car_data.get("configuration_info", {}).items():
            self._draw_text_block(f"{k}: {v}", font_size, line_spacing)

    def draw_images_from_dir(self, images_dir="car_data"):
        """Draw all images from directory, handling page breaks."""
        if not Path(images_dir).exists():
            return
        self.c.showPage()
        for f in os.listdir(images_dir):
            if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                continue
            img_path = os.path.join(images_dir, f)
            with Image.open(img_path) as im:
                w, h = im.size
                aspect = w / h
                dh = self.width / aspect
                if self.y_cursor - dh < 0:
                    self.c.showPage()
                    self.y_cursor = self.height - dh
                self.c.drawImage(img_path, 0, self.y_cursor,
                                    width=self.width, height=dh)
                self.y_cursor -= dh + DEFAULT_IMAGE_SPACING

    def save(self):
        """Finalize and save PDF."""
        self.c.showPage()
        self.c.save()

    def _draw_text_block(self, text: str, font_size=DEFAULT_FONT_SIZE,
                         line_spacing=DEFAULT_LINE_SPACING):
        """Draw wrapped text lines at current cursor with page breaks."""
        wrapped_lines = simpleSplit(
            text, self.font_name, font_size, self.width - 2 * self.margin
        )
        for line in wrapped_lines:
            if self.y_cursor < self.margin:
                self.c.showPage()
                self.y_cursor = self.height - self.margin
                self.c.setFont(self.font_name, font_size)
            self.c.drawString(self.margin, self.y_cursor, line)
            self.y_cursor -= line_spacing


def create_pdf(json_path="car_data/info.json", output_pdf="Auto.pdf",
               font_name=DEFAULT_FONT_NAME, font_path=DEFAULT_FONT_PATH):
    """Create PDF from car JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        car_data = json.load(f)
    writer = PDFWriter(output_pdf)
    writer.register_font(font_name, font_path)
    writer.draw_car_info(car_data)
    writer.draw_images_from_dir("car_data")
    writer.save()
