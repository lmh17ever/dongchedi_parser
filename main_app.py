"""
Original Author: Father1993  
Modified By: lmh17ever

A Tkinter-based GUI application for parsing car data from DongCheDi pages.

This module provides the `CarParserApp` class, which allows users to input
a URL for a car listing, parse the car information using `CarParser`, 
display the results in a scrollable text area, and generate a PDF of the data.

Features:
- Threaded parsing to keep the GUI responsive.
- Progress bar to indicate parsing status.
- Queue-based communication between background thread and UI.
- JSON display of car data.
- PDF generation via `create_pdf`.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread
from queue import Queue

from main_page_parser import CarParser
from pdf_creator import create_pdf


class CarParserApp:
    """GUI application for parsing DongCheDi car pages."""

    POLL_INTERVAL = 100  # ms

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("DongCheDi Car Parser")
        self.root.geometry("800x600")

        self.parser = CarParser()
        self.queue = Queue()

        self._build_ui()
        self.root.after(self.POLL_INTERVAL, self._process_queue)

    # ----------------------------
    # UI
    # ----------------------------

    def _build_ui(self):
        """Initialize all UI elements."""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main_frame, text="Enter car page URL:")\
           .grid(row=0, column=0, sticky="w", pady=5)

        self.url_entry = ttk.Entry(main_frame, width=60)
        self.url_entry.grid(row=1, column=0, sticky="we", pady=5)

        self.parse_button = ttk.Button(
            main_frame, text="Parse", command=self._start_parsing
        )
        self.parse_button.grid(row=2, column=0, sticky="w", pady=10)

        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(row=3, column=0, sticky="we", pady=5)

        self.result_text = scrolledtext.ScrolledText(main_frame, height=20, width=70)
        self.result_text.grid(row=4, column=0, sticky="nsew", pady=5)

    # ----------------------------
    # Parsing
    # ----------------------------

    def _start_parsing(self):
        """Start parsing in a background thread."""
        url = self.url_entry.get().strip()
        if not url:
            self._append_text("Please enter a URL.")
            return

        self._lock_ui()
        self._append_text("Parsing started...")

        thread = Thread(target=self._parse_worker, args=(url,), daemon=True)
        thread.start()

    def _parse_worker(self, url: str):
        """Background thread for parsing the car page."""
        try:
            parser = CarParser(queue=self.queue)
            parser.parse_car_page(url)
            create_pdf(main_app_flag=True)
            self._put("message", "PDF file created!")

        except Exception as e:
            self._put("message", f"Error occurred: {e}")
            raise

        finally:
            self._put("finish", None)

    # ----------------------------
    # Queue Handling
    # ----------------------------

    def _process_queue(self):
        """Process messages from the worker thread."""
        while not self.queue.empty():
            action, data = self.queue.get()

            if action == "message":
                self._append_text(data)

            elif action == "finish":
                self._unlock_ui()

        self.root.after(self.POLL_INTERVAL, self._process_queue)

    def _put(self, action, data):
        """Add a message to the processing queue."""
        self.queue.put((action, data))

    # ----------------------------
    # UI Helpers
    # ----------------------------

    def _append_text(self, msg: str):
        """Append message to the text output area."""
        self.result_text.insert(tk.END, msg + "\n")
        self.result_text.see(tk.END)

    def _lock_ui(self):
        """Disable UI during parsing."""
        self.parse_button.config(state="disabled")
        self.progress.start()
        self.result_text.delete(1.0, tk.END)

    def _unlock_ui(self):
        """Re-enable UI after parsing."""
        self.progress.stop()
        self.parse_button.config(state="normal")


# ----------------------------
# App Start
# ----------------------------

if __name__ == "__main__":
    window = tk.Tk()
    app = CarParserApp(window)
    window.mainloop()
