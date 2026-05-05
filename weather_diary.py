import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("800x500")
        
        # Список всех записей
        self.records = []
        
        # Имя файла для сохранения
        self.filename = "weather_diary.json"
        
        # Переменные для полей ввода
        self.date_var = tk.StringVar()
        self.temp_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.precip_var = tk.BooleanVar(value=False)
        
        # Переменные для фильтров
        self.filter_date_var = tk.StringVar()
        self.filter_temp_var = tk.StringVar()
        
        # Загрузка данных из файла при запуске
        self.load_from_json()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Отображение всех записей
        self.update_display()
    
    def create_widgets(self):
        # Рамка для ввода новой записи
        input_frame = ttk.LabelFrame(self.root, text="Новая запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.temp_var, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        # Описание
        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.desc_var, width=40).grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="ew")
        
        # Осадки (чекбокс)
        ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        
        # Кнопка "Добавить запись"
        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(row=2, column=1, padx=5, pady=2)
        
        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(filter_frame, textvariable=self.filter_date_var, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(filter_frame, text="Фильтровать по дате", command=lambda: self.filter_records("date")).grid(row=0, column=2, padx=5)
        
        # Фильтр по температуре (> заданного значения)
        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(filter_frame, textvariable=self.filter_temp_var, width=10).grid(row=1, column=1, padx=5)
        ttk.Button(filter_frame, text="Фильтровать по температуре", command=lambda: self.filter_records("temp")).grid(row=1, column=2, padx=5)
        
        # Кнопка сброса фильтров
        ttk.Button(filter_frame, text="Показать все записи", command=self.clear_filters).grid(row=2, column=0, columnspan=3, pady=5)
        
        # Таблица для отображения записей
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создаём Treeview с колонками
        self.tree = ttk.Treeview(table_frame, columns=("date", "temp", "desc", "precip"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")
        self.tree.column("date", width=100)
        self.tree.column("temp", width=100)
        self.tree.column("desc", width=300)
        self.tree.column("precip", width=80)
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления данными
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_from_json).pack(side="left", padx=5)
    
    def add_record(self):
        """Добавление новой записи после проверки ввода"""
        date_str = self.date_var.get().strip()
        temp_str = self.temp_var.get().strip()
        description = self.desc_var.get().strip()
        precipitation = self.precip_var.get()
        
        # Проверка даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД (например, 2025-03-30)")
            return
        
        # Проверка температуры
        try:
            temperature = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом (целым или дробным)")
            return
        
        # Проверка описания
        if not description:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым")
            return
        
        # Создание записи
        record = {
            "date": date_str,
            "temperature": temperature,
            "description": description,
            "precipitation": precipitation
        }
        self.records.append(record)
        
        # АВТОМАТИЧЕСКИ СОХРАНЯЕМ В JSON ПОСЛЕ ДОБАВЛЕНИЯ
        self.save_to_json(show_message=False)
        
        # Очистка полей ввода
        self.date_var.set("")
        self.temp_var.set("")
        self.desc_var.set("")
        self.precip_var.set(False)
        
        # Сброс фильтров и обновление отображения
        self.clear_filters()
        messagebox.showinfo("Успех", "Запись добавлена и сохранена в JSON")
    
    def filter_records(self, filter_type):
        """Применение фильтрации по дате или температуре"""
        filtered = self.records[:]  # копия всех записей
        
        # Фильтр по дате
        if filter_type == "date" or (filter_type == "both" and self.filter_date_var.get().strip()):
            filter_date = self.filter_date_var.get().strip()
            if filter_date:
                try:
                    datetime.strptime(filter_date, "%Y-%m-%d")
                    filtered = [r for r in filtered if r["date"] == filter_date]
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверный формат даты фильтра. Используйте ГГГГ-ММ-ДД")
                    return
        
        # Фильтр по температуре (> заданного значения)
        if filter_type == "temp" or (filter_type == "both" and self.filter_temp_var.get().strip()):
            filter_temp_str = self.filter_temp_var.get().strip()
            if filter_temp_str:
                try:
                    min_temp = float(filter_temp_str)
                    filtered = [r for r in filtered if r["temperature"] > min_temp]
                except ValueError:
                    messagebox.showerror("Ошибка", "Температура фильтра должна быть числом")
                    return
        
        self.update_display(filtered)
    
    def clear_filters(self):
        """Сброс всех фильтров и отображение всех записей"""
        self.filter_date_var.set("")
        self.filter_temp_var.set("")
        self.update_display(self.records)
    
    def update_display(self, records_to_show=None):
        """Обновление Treeview указанным списком записей"""
        # Удаляем все текущие строки
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        if records_to_show is None:
            records_to_show = self.records
        
        # Заполняем таблицу
        for rec in records_to_show:
            precip_text = "Да" if rec["precipitation"] else "Нет"
            self.tree.insert("", "end", values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                precip_text
            ))
    
    def save_to_json(self, show_message=True):
        """Сохранение всех записей в JSON-файл"""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            if show_message:
                messagebox.showinfo("Успех", f"Данные сохранены в {self.filename}")
        except Exception as e:
            if show_message:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def load_from_json(self, show_message=True):
        """Загрузка записей из JSON-файла"""
        if not os.path.exists(self.filename):
            if show_message:
                messagebox.showwarning("Предупреждение", f"Файл {self.filename} не найден. Будет создан новый при добавлении записей.")
            return
        
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    self.records = loaded
                    self.clear_filters()   # обновляем отображение
                    if show_message:
                        messagebox.showinfo("Загрузка", f"Загружено {len(self.records)} записей из {self.filename}")
                else:
                    if show_message:
                        messagebox.showerror("Ошибка", "Файл имеет неверный формат")
        except Exception as e:
            if show_message:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()