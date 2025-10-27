"""Creating interface for app"""

import json
import tkinter as tk
from tkinter import ttk, scrolledtext, Canvas, VERTICAL

from configuration_parser import get_data


class AutoParserApp:
    """Главный класс приложения авто-парсера"""

    CONFIG_FILE = 'config.json'
    TRANSLATION_FILE = 'test_names_translation.json'

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Dongchedi парсер")

        # Группировка атрибутов
        self.ui = self.UIContainer()
        self.state = self.StateContainer()

        self._load_config()
        self._create_widgets()
        self._setup_bindings()

    class UIContainer:
        """Контейнер для UI элементов"""
        def __init__(self):
            self.notebook = None
            self.tabs = {
                'get_data': None,
                'parameters': None, 
                'config': None
            }
            self.input_entry = None
            self.output_text = None
            self.scroll_elements = {
                'canvas': None,
                'scrollbar': None,
                'frame': None
            }
            self.buttons_frame = None

    class StateContainer:
        """Контейнер для состояния приложения"""
        def __init__(self):
            self.with_empty_parameters = tk.IntVar()
            self.parameter_vars = {}
            self.parameters_dict = {}

    def _load_config(self):
        """Загрузка конфигурации из файлов"""
        with open(self.CONFIG_FILE, 'r', encoding='utf-8') as file:
            config = json.load(file)
            self.state.with_empty_parameters.set(config['with_empty_parameters'])

        with open(self.TRANSLATION_FILE, 'r', encoding='utf-8') as file:
            self.state.parameters_dict = json.load(file)

    def _create_widgets(self):
        """Создание всех виджетов интерфейса"""
        self._create_notebook()
        self._create_get_data_tab()
        self._create_parameters_tab()
        self._create_config_tab()

    def _create_notebook(self):
        """Создание блокнота с вкладками"""
        self.ui.notebook = ttk.Notebook(self.window)

        self.ui.tabs['get_data'] = ttk.Frame(self.ui.notebook)
        self.ui.tabs['parameters'] = ttk.Frame(self.ui.notebook)
        self.ui.tabs['config'] = ttk.Frame(self.ui.notebook)

        self.ui.notebook.add(self.ui.tabs['get_data'], text='Получить данные')
        self.ui.notebook.add(self.ui.tabs['parameters'], text='Список параметров')
        self.ui.notebook.add(self.ui.tabs['config'], text='Настройки')
        self.ui.notebook.pack(expand=True, fill="both")

    def _create_get_data_tab(self):
        """Создание вкладки для получения данных"""
        tab = self.ui.tabs['get_data']

        input_label = tk.Label(tab, text="Нажимайте Ctrl+V и Ctrl+C со включенной английской раскладкой\nВставьте ссылку:")
        input_label.pack(pady=10)

        self.ui.input_entry = tk.Entry(tab, width=100)
        self.ui.input_entry.pack(pady=10)

        submit_button = tk.Button(
            tab,
            text="Получить данные",
            command=self.parse_page
        )
        submit_button.pack(pady=10)

        self.ui.output_text = scrolledtext.ScrolledText(tab, width=100, height=40)
        self.ui.output_text.pack(pady=10)

    def _create_parameters_tab(self):
        """Создание вкладки со списком параметров"""
        self._create_parameters_buttons_tab()
        self._create_scrollable_frame()
        self._create_parameter_checkboxes()

    def _create_parameters_buttons_tab(self):
        buttons_frame = ttk.Frame(self.ui.tabs['parameters'], height=40)
        buttons_frame.pack(anchor='nw')

        select_all_btn = ttk.Button(
            buttons_frame,
            text="Выбрать все",
            command=self._select_all_parameters,
            width=15
        )
        select_all_btn.pack(side='left', padx=5, pady=5)

        deselect_all_btn = ttk.Button(
            buttons_frame,
            text="Снять все",
            command=self._deselect_all_parameters
        )
        deselect_all_btn.pack(side='left', padx=5, pady=5)

        # Сохраняем ссылку на фрейм кнопок если понадобится
        self.ui.buttons_frame = buttons_frame

    def _create_scrollable_frame(self):
        """Создание прокручиваемой области для параметров"""
        tab = self.ui.tabs['parameters']

        self.ui.scroll_elements['canvas'] = Canvas(tab)
        self.ui.scroll_elements['scrollbar'] = ttk.Scrollbar(
            tab,
            orient=VERTICAL,
            command=self.ui.scroll_elements['canvas'].yview
        )
        self.ui.scroll_elements['frame'] = ttk.Frame(self.ui.scroll_elements['canvas'])

        canvas = self.ui.scroll_elements['canvas']
        scrollable_frame = self.ui.scroll_elements['frame']

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=self.ui.scroll_elements['scrollbar'].set)

        canvas.pack(side="left", fill="both", expand=True)
        self.ui.scroll_elements['scrollbar'].pack(side="right", fill="y")

    def _create_parameter_checkboxes(self):
        """Создание чекбоксов для параметров"""
        scrollable_frame = self.ui.scroll_elements['frame']

        for parameter, value in self.state.parameters_dict.items():
            var = tk.IntVar(value=value[1])
            self.state.parameter_vars[parameter] = var

            checkbox = tk.Checkbutton(
                scrollable_frame,
                text=value[0],
                variable=var,
                command=lambda p=parameter, v=var: self._on_parameter_change(p, v.get())
            )
            checkbox.pack(anchor='nw', padx=10)

    def _create_config_tab(self):
        """Создание вкладки настроек"""
        checkbox = tk.Checkbutton(
            self.ui.tabs['config'],
            text='Учитывать отсутствующие параметры',
            variable=self.state.with_empty_parameters,
            command=self._on_empty_parameters_change
        )
        checkbox.pack()

    def _setup_bindings(self):
        """Настройка привязок событий"""
        canvas = self.ui.scroll_elements['canvas']
        if canvas:
            canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def parse_page(self):
        """Обработка события при нажатии кнопки <<Получить данные>>"""
        url = self.ui.input_entry.get()
        result = get_data(url)
        self._display_result(str(result))


    def _display_result(self, result):
        """Отображение результата в текстовом поле"""
        self.ui.output_text.delete("1.0", tk.END)
        self.ui.output_text.insert(tk.END, result)

    def _select_all_parameters(self):
        """Выбрать все параметры"""
        for parameter, var in self.state.parameter_vars.items():
            var.set(1)
            self._on_parameter_change(parameter, 1)

    def _deselect_all_parameters(self):
        """Снять выбор со всех параметров"""
        for parameter, var in self.state.parameter_vars.items():
            var.set(0)
            self._on_parameter_change(parameter, 0)

    def _on_empty_parameters_change(self):
        """Обработчик изменения флага учитывания пустых параметров"""
        self._update_config_file(
            self.CONFIG_FILE,
            {'with_empty_parameters': self.state.with_empty_parameters.get()}
        )

    def _on_parameter_change(self, parameter_name, value):
        """Обработчик изменения параметра"""
        self.state.parameters_dict[parameter_name][1] = value
        self._update_config_file(
            self.TRANSLATION_FILE,
            self.state.parameters_dict,
            ensure_ascii=False,
            indent=4
        )

    def _update_config_file(self, filename, data, **json_kwargs):
        """Обновление конфигурационного файла"""
        with open(filename, 'r+', encoding='utf-8') as file:
            file_data = json.load(file)
            file_data.update(data)
            file.seek(0)
            json.dump(file_data, file, **json_kwargs)
            file.truncate()

    def _on_mousewheel(self, event):
        """Обработчик прокрутки колесика мыши"""
        canvas = self.ui.scroll_elements['canvas']
        if canvas:
            if event.delta > 0 or event.num == 4:
                canvas.yview_scroll(-1, 'units')
            else:
                canvas.yview_scroll(1, 'units')

    def run(self):
        """Запуск приложения"""
        self.window.mainloop()


if __name__ == "__main__":
    app = AutoParserApp()
    app.run()
