import tkinter as tk
from tkinter import ttk, messagebox
import json

DATA_FILE = "vehicles.json"

def load_vehicles():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_vehicle(vehicle):
    vehicles = load_vehicles()
    vehicles.append(vehicle)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(vehicles, f, ensure_ascii=False, indent=2)

def delete_vehicle_by_vin(vin):
    vehicles = load_vehicles()
    vehicles = [v for v in vehicles if v["vin"] != vin]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(vehicles, f, ensure_ascii=False, indent=2)

root = tk.Tk()
root.title("Автокъща")
root.geometry("1000x600")

columns = ("make", "model", "year", "color", "price", "vin", "mileage", "fuel", "gearbox", "reg_number")

tree = ttk.Treeview(root, columns=columns, show="headings")

headers = {
    "make": "Марка",
    "model": "Модел",
    "year": "Година",
    "color": "Цвят",
    "price": "Цена (лв)",
    "vin": "Рам номер",
    "mileage": "Пробег (км)",
    "fuel": "Гориво",
    "gearbox": "Скорости",
    "reg_number": "Рег. номер"
}

for col in columns:
    tree.heading(col, text=headers[col])
    tree.column(col, width=100)

tree.pack(expand=True, fill="both", padx=10, pady=10)

def reload_tree(data=None):
    for i in tree.get_children():
        tree.delete(i)
    dataset = data if data is not None else load_vehicles()
    for vehicle in dataset:
        tree.insert("", "end", values=tuple(vehicle.get(col, "") for col in columns))

reload_tree()

def open_add_vehicle_window():
    add_window = tk.Toplevel(root)
    add_window.title("Добави нова кола")
    add_window.geometry("500x600")

    vehicle_labels = {
        "make": "Марка", "model": "Модел", "year": "Година", "color": "Цвят",
        "price": "Цена", "vin": "Рам номер", "mileage": "Пробег (км)",
        "fuel": "Тип гориво", "gearbox": "Скоростна кутия", "reg_number": "Рег. номер"
    }

    client_labels = {
        "customer_name": "Име на клиент",
        "customer_phone": "Телефон",
        "customer_email": "Имейл"
    }

    entries = {}

    row = 0
    for key in vehicle_labels:
        tk.Label(add_window, text=vehicle_labels[key]).grid(row=row, column=0, pady=5, sticky="e")
        entry = tk.Entry(add_window)
        entry.grid(row=row, column=1, pady=5)
        entries[key] = entry
        row += 1

    for key in client_labels:
        tk.Label(add_window, text=client_labels[key]).grid(row=row, column=0, pady=5, sticky="e")
        entry = tk.Entry(add_window)
        entry.grid(row=row, column=1, pady=5)
        entries[key] = entry
        row += 1

    def save_new_vehicle():
        new_vehicle = {}
        for key in vehicle_labels:
            value = entries[key].get().strip()
            if not value:
                messagebox.showwarning("Грешка", f"Попълнете: {vehicle_labels[key]}")
                return
            new_vehicle[key] = value

        # Добавяме и клиентските данни
        for key in client_labels:
            new_vehicle[key] = entries[key].get().strip()

        save_vehicle(new_vehicle)
        reload_tree()
        add_window.destroy()

    tk.Button(add_window, text="Запази", command=save_new_vehicle).grid(row=row, column=0, columnspan=2, pady=20)

def delete_selected_vehicle():
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Изтриване", "Изберете кола за изтриване.")
        return

    confirm = messagebox.askyesno("Потвърждение", "Сигурни ли сте?")
    if not confirm:
        return

    vin = tree.item(selected[0], "values")[5]
    delete_vehicle_by_vin(vin)
    tree.delete(selected[0])

def show_customer_info():
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Клиент", "Изберете кола, за да видите клиента.")
        return

    vin = tree.item(selected[0], "values")[5]
    vehicles = load_vehicles()
    for v in vehicles:
        if v["vin"] == vin:
            info = (
                f"Име: {v.get('customer_name', 'Няма')}\n"
                f"Телефон: {v.get('customer_phone', 'Няма')}\n"
                f"Имейл: {v.get('customer_email', 'Няма')}"
            )
            messagebox.showinfo("Клиент", info)
            break

# Бутоните
tk.Button(root, text="Добави кола", command=open_add_vehicle_window).pack(pady=5)
tk.Button(root, text="Изтрий кола", command=delete_selected_vehicle).pack(pady=5)
tk.Button(root, text="Покажи клиент", command=show_customer_info).pack(pady=5)

# Търсене
search_frame = tk.Frame(root)
search_frame.pack(pady=10)

tk.Label(search_frame, text="Търси по марка или модел:").pack(side="left")
search_entry = tk.Entry(search_frame)
search_entry.pack(side="left", padx=5)

def search_vehicles():
    query = search_entry.get().strip().lower()
    tree.delete(*tree.get_children())
    for v in load_vehicles():
        if query in v["make"].lower() or query in v["model"].lower():
            tree.insert("", "end", values=tuple(v[col] for col in columns))


# Филтриране по цена
price_filter_frame = tk.Frame(root)
price_filter_frame.pack(pady=5)

tk.Label(price_filter_frame, text="Мин. цена:").pack(side="left")
min_price_entry = tk.Entry(price_filter_frame, width=10)
min_price_entry.pack(side="left", padx=5)

tk.Label(price_filter_frame, text="Макс. цена:").pack(side="left")
max_price_entry = tk.Entry(price_filter_frame, width=10)
max_price_entry.pack(side="left", padx=5)

def filter_by_price():
    try:
        min_price = int(min_price_entry.get()) if min_price_entry.get() else 0
        max_price = int(max_price_entry.get()) if max_price_entry.get() else 9999999
    except ValueError:
        messagebox.showerror("Грешка", "Моля въведете валидни стойности за цената.")
        return

    filtered_vehicles = [
        vehicle for vehicle in load_vehicles()
        if min_price <= int(vehicle.get("price", 0)) <= max_price
    ]

    reload_tree(filtered_vehicles)

filter_button = tk.Button(price_filter_frame, text="Филтрирай по цена", command=filter_by_price)
filter_button.pack(side="left", padx=10)


tk.Button(search_frame, text="Търси", command=search_vehicles).pack(side="left", padx=5)
tk.Button(search_frame, text="Покажи всички", command=reload_tree).pack(side="left", padx=5)

root.mainloop()
