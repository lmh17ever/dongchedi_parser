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
    """Компактный генератор PDF с внутренним курсором"""

    def __init__(self, output_pdf: str, page_size=DEFAULT_PAGE_SIZE,
                 margin=DEFAULT_MARGIN):
        self.output_pdf = output_pdf
        self.width, self.height = page_size
        self.margin = margin
        self.y_cursor = self.height - margin
        self.c = canvas.Canvas(output_pdf, pagesize=page_size)
        self.font_name = DEFAULT_FONT_NAME

    def register_font(self, font_name=DEFAULT_FONT_NAME, font_path=DEFAULT_FONT_PATH):
        """Регистрация TTF-шрифта"""
        if font_path and os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            self.font_name = font_name
        self.c.setFont(self.font_name, DEFAULT_FONT_SIZE)

    def draw_car_info(self, main_app_flag, car_data, font_size=DEFAULT_FONT_SIZE,
                      line_spacing=DEFAULT_LINE_SPACING):
        """Вывод заголовка, пробега и характеристик"""
        if main_app_flag:
            # Предполагаем, что в car_data есть title и mileage
            title = car_data.get("title", "Без названия")
            self._draw_text_block(title, font_size + 4, line_spacing + 2)  # чуть крупнее

            mileage = car_data.get("mileage", 0)
            self._draw_text_block(f"Пробег: {int(mileage * 10000):,} км",
                                font_size, line_spacing)

            # Характеристики теперь ожидаются в виде списка словарей
            config_items = car_data.get("configuration_info", [])
        else:
            # когда main_app_flag=False → car_data уже является списком характеристик
            config_items = car_data

        # Выводим все пары name: value
        for item in config_items:
            name = item.get("name", "—")
            value = item.get("value", "—")
            self._draw_text_block(f"{name}: {value}", font_size, line_spacing)

    def draw_images_from_dir(self, images_dir="car_data"):
        """Вставка всех изображений из папки с автоматическим разрывом страниц"""
        if not Path(images_dir).exists():
            return

        self.y_cursor = -1  # -1 → принудительный разрыв страницы перед первой картинкой

        for fname in sorted(os.listdir(images_dir)):
            if not fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                continue

            img_path = os.path.join(images_dir, fname)
            try:
                with Image.open(img_path) as im:
                    w, h = im.size
                    aspect = w / h
                    draw_height = self.width / aspect   # сохраняем пропорции

                    if self.y_cursor - draw_height < self.margin * 1.5:
                        self.c.showPage()
                        self.y_cursor = self.height - self.margin

                    self.c.drawImage(img_path,
                                     x=0,
                                     y=self.y_cursor - draw_height,
                                     width=self.width,
                                     height=draw_height,
                                     preserveAspectRatio=True)

                    self.y_cursor -= draw_height + DEFAULT_IMAGE_SPACING

            except Exception as e:
                print(f"Ошибка при вставке {fname}: {e}")

    def save(self):
        """Завершение и сохранение PDF"""
        if self.y_cursor < self.height - 10:  # была хоть какая-то информация на странице
            self.c.showPage()
        self.c.save()

    def _draw_text_block(self, text: str, font_size=DEFAULT_FONT_SIZE,
                         line_spacing=DEFAULT_LINE_SPACING):
        """Вывод многострочного текста с переносами и разрывом страниц"""
        self.c.setFont(self.font_name, font_size)

        wrapped = simpleSplit(text, self.font_name, font_size,
                              self.width - 2 * self.margin)

        for line in wrapped:
            if self.y_cursor - line_spacing < self.margin:
                self.c.showPage()
                self.y_cursor = self.height - self.margin
                self.c.setFont(self.font_name, font_size)

            self.c.drawString(self.margin, self.y_cursor, line)
            self.y_cursor -= line_spacing


def create_pdf(main_app_flag=False, car_data=None,
               json_path="car_data/info.json", output_pdf="Auto.pdf",
               font_name=DEFAULT_FONT_NAME, font_path=DEFAULT_FONT_PATH):
    """Создание PDF из данных автомобиля"""
    writer = PDFWriter(output_pdf)
    writer.register_font(font_name, font_path)

    if car_data is None:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                car_data = json.load(f)
        except Exception as e:
            print(f"Ошибка чтения JSON: {e}")
            return

    writer.draw_car_info(main_app_flag, car_data)
    
    if main_app_flag:
        writer.draw_images_from_dir("car_data")
        
    writer.save()
