# main.py
import tkinter as tk
from customtkinter import *
import storage
import basket
from PIL import Image, ImageTk
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import gc  # garbace collecter

# Set the Theme
set_default_color_theme("dark-blue")
set_appearance_mode("Dark")

storage.initialize_db()
storage.load_data()

# Initialize the main application
app = CTk()
app.geometry("1920x1080")
app.attributes("-fullscreen", False)
app.title("Envanter Takip Sistemi")

# Set the window icon
app.iconbitmap("assets/icon.ico")

main_frame = CTkFrame(app)
main_frame.pack(fill="both", expand=True)

left_frame = CTkFrame(main_frame)
right_frame = CTkFrame(main_frame)

left_frame.pack(side="left", fill="both", expand=True)
right_frame.pack(side="right", fill="both", expand=True)

search_bar = CTkEntry(
    left_frame,
    placeholder_text="Ürünlerde Ara",
    font=("Arial", 24),
    justify="center",
    width=716,
)
search_bar.pack(padx=10, pady=20, fill="x")

search_results_frame = CTkFrame(left_frame)
search_results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))

search_canvas = tk.Canvas(
    search_results_frame, borderwidth=0, highlightthickness=0, bg="#2B2B2B"
)
search_scrollbar = CTkScrollbar(
    search_results_frame, orientation="vertical", command=search_canvas.yview
)
search_scrollable_frame = CTkFrame(search_canvas, fg_color="transparent")


def configure_scrollregion(event):
    search_canvas.configure(scrollregion=search_canvas.bbox("all"))


search_scrollable_frame.bind("<Configure>", configure_scrollregion)

search_canvas.create_window((0, 0), window=search_scrollable_frame, anchor="nw")

search_canvas.configure(yscrollcommand=search_scrollbar.set)

search_canvas.pack(side="left", fill="both", expand=True)
search_scrollbar.pack(side="right", fill="y")

add_product_button = CTkButton(
    left_frame,
    text="Ürün Ekle",
    font=("Arial", 24),
    command=lambda: open_add_product_window(),
)
add_product_button.pack(padx=10, pady=20, side="bottom")

total_value_frame = CTkFrame(right_frame)
total_value_frame.pack(pady=(20, 5), padx=10, fill="x")

total_value_label = CTkLabel(
    total_value_frame, text="Toplam: 0.00₺", font=("Arial", 24, "bold")
)
total_value_label.pack(side="left", padx=10, pady=5, expand=True)

print_icon_image = Image.open("assets/print_icon.png")
print_icon = CTkImage(light_image=print_icon_image, dark_image=print_icon_image)
print_basket_button = CTkButton(
    total_value_frame,
    image=print_icon,
    text="",
    font=("Arial", 24),
    width=50,
    height=34,
    command=lambda: basket.print_basket(),
)
print_basket_button.pack(side="right", padx=2, pady=0)

basket_frame_container = CTkFrame(right_frame)
basket_frame_container.pack(fill="both", expand=True, padx=10, pady=(20, 20))

basket_canvas = tk.Canvas(
    basket_frame_container, borderwidth=0, highlightthickness=0, bg="#2B2B2B"
)
basket_scrollbar = CTkScrollbar(
    basket_frame_container, orientation="vertical", command=basket_canvas.yview
)
basket_scrollable_frame = CTkFrame(basket_canvas, fg_color="transparent")

basket_scrollable_frame.bind(
    "<Configure>",
    lambda e: basket_canvas.configure(scrollregion=basket_canvas.bbox("all")),
)

basket_canvas.create_window((0, 0), window=basket_scrollable_frame, anchor="nw")
basket_canvas.configure(yscrollcommand=basket_scrollbar.set)

basket_canvas.pack(side="left", fill="both", expand=True)
basket_scrollbar.pack(side="right", fill="y")

confirm_order_button = CTkButton(
    right_frame,
    text="Siparişi Onayla",
    font=("Arial", 24),
    command=lambda: confirm_order(),
)
confirm_order_button.pack(padx=10, pady=20, side="bottom")


def update_basket_display():
    for widget in basket_scrollable_frame.winfo_children():
        widget.destroy()

    for item in basket.get_basket_items():
        item_frame = CTkFrame(basket_scrollable_frame)
        item_frame.pack(fill="x", padx=0, pady=0)

        remove_button = CTkButton(
            item_frame,
            text="—",
            command=lambda name=item["name"]: remove_from_basket(name),
            font=("Arial", 10, "bold"),
            width=40,
            height=20,
        )
        remove_button.pack(side="left", padx=0)

        item_label = CTkLabel(
            item_frame,
            text=f"{item['name']} - {item['price']:.2f}₺",
            font=("Arial", 16),
            width=440,
        )
        item_label.pack(side="left")

        amount_entry = CTkEntry(item_frame, font=("Arial", 14), width=50, height=20)
        amount_entry.pack(side="right", padx=0)
        amount_entry.insert(0, str(item["amount"]))

        def delayed_update(event, name=item["name"], entry=amount_entry):
            try:
                amount = float(entry.get())
                app.after(2000, lambda: update_amount(name, amount))
            except ValueError:
                pass

        amount_entry.bind(
            "<KeyRelease>",
            lambda event, name=item["name"], entry=amount_entry: delayed_update(
                event, name, entry
            ),
        )

    total_value_label.configure(text=f"Toplam: {basket.get_total_value():.2f}₺")


def add_to_basket(item_name):
    item_price = storage.get_item_price(item_name)
    basket.add_to_basket(item_name, item_price)
    update_basket_display()


def remove_from_basket(item_name):
    basket.remove_from_basket(item_name)
    update_basket_display()


def update_amount(item_name, amount):
    try:
        amount = float(amount)
        basket.update_item_amount(item_name, amount)
        update_basket_display()
    except ValueError:
        pass


def update_stock(item_name, new_stock):
    try:
        new_stock = int(new_stock)
        storage.update_product_stock(item_name, new_stock)
        search_items()
    except ValueError:
        pass


result_frame = CTkFrame(search_scrollable_frame)
result_frame.pack(fill="both", expand=True, padx=0, pady=0)

result_frame.grid_columnconfigure(0, weight=1)
result_frame.grid_columnconfigure(1, weight=3)
result_frame.grid_columnconfigure(2, weight=1)
result_frame.grid_columnconfigure(3, weight=1)
result_frame.grid_columnconfigure(4, weight=1)

CTkLabel(
    result_frame,
    text="Barkod",
    anchor="w",
    padx=5,
    font=("Arial", 20, "bold"),
    width=220,
).grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
CTkLabel(
    result_frame, text="İsim", anchor="w", padx=5, font=("Arial", 20, "bold"), width=435
).grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
CTkLabel(
    result_frame, text="Stok", anchor="w", padx=5, font=("Arial", 20, "bold"), width=80
).grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
CTkLabel(
    result_frame, text="Fiyat", anchor="w", padx=5, font=("Arial", 20, "bold"), width=105
).grid(row=0, column=3, sticky="nsew", padx=5, pady=5)
CTkLabel(
    result_frame, text="", anchor="w", padx=5, font=("Arial", 20, "bold"), width=40
).grid(row=0, column=4, sticky="nsew", padx=5, pady=5)

search_thread = None
search_cancelled = False
search_paused = threading.Event()
search_paused.set()
loading = False

executor = ThreadPoolExecutor(max_workers=4)
ui_queue = queue.Queue()
update_scheduled = False

idle_time = 0
idle_threshold = 300
app_paused = False


def reset_idle_timer(event=None):
    global idle_time, app_paused
    idle_time = 0
    if app_paused:
        resume_app()


def check_idle():
    global idle_time, app_paused
    idle_time += 1
    if idle_time >= idle_threshold and not app_paused:
        pause_app()
    app.after(1000, check_idle)


def pause_app():
    global app_paused
    app_paused = True
    search_paused.clear()
    trigger_garbage_collection()


def resume_app():
    global app_paused
    app_paused = False
    search_paused.set()
    app.after(100, process_queue)


def process_queue():
    global app_paused
    if app_paused:
        return
    try:
        while True:
            task = ui_queue.get_nowait()
            task()
    except queue.Empty:
        pass
    finally:
        if not app_paused:
            app.after(200, process_queue)


app.after(200, process_queue)


def trigger_garbage_collection():
    gc.collect()


app.bind_all("<Motion>", reset_idle_timer)
app.bind_all("<Key>", reset_idle_timer)
app.bind_all("<Button>", reset_idle_timer)
app.after(1000, check_idle)

matched_items = []
items_per_page = 20
current_page = 0
row_index = 1


def search_items(event=None):
    global search_thread, search_cancelled, update_scheduled, items_per_page

    for widget in result_frame.winfo_children():
        grid_info = widget.grid_info()
        if "row" in grid_info and grid_info["row"] != 0:
            widget.destroy()

    query = search_bar.get().lower()
    items_per_page = 20

    if search_thread and not search_thread.done():
        search_cancelled = True
        search_thread.cancel()

    def calculate_match_position(item_lower, query_lower):
        words = item_lower.split()
        for idx, word in enumerate(words):
            if word.startswith(query_lower):
                return idx
        return len(words)

    def searching(event=None):
        nonlocal query
        global matched_items, current_page, items_per_page
        current_page = 0
        items_per_page = 20

        if search_cancelled:
            return

        temp_matched_items = []
        all_items = storage.load_data()
        for item in all_items:
            if search_cancelled:
                return

            search_paused.wait()

            item_barcode, item_name, item_price, item_stock = item

            item_lower = item_name.lower()
            barcode_lower = item_barcode.lower()
            query_lower = query.lower()

            if query_lower in item_lower or query_lower == barcode_lower:
                match_position = calculate_match_position(item_lower, query_lower)
                temp_matched_items.append(
                    (match_position, item_barcode, item_name, item_stock, item_price)
                )

        temp_matched_items.sort(key=lambda x: x[0])

        with threading.Lock():
            search_canvas.yview_moveto(0)
            matched_items = temp_matched_items

        ui_queue.put(update_widgets)

    def update_widgets():
        global search_cancelled, loading, matched_items, current_page, items_per_page, update_scheduled

        if loading:
            return

        loading = True

        search_bar.unbind("<KeyPress-Return>")

        def add_first_item(event=None):
            if matched_items:
                first_item = matched_items[0][2]
                add_to_basket(first_item)
            search_bar.delete(0, END)
            search_bar.unbind("<KeyPress-Return>")
            search_items()

        search_bar.bind(
            "<KeyPress-Return>",
            lambda event: ui_queue.put(lambda: app.after(500, add_first_item)),
        )

        editing = False

        def make_entry(event, field, value, idx, label_widget, item_name, row):
            nonlocal editing
            if editing:
                return
            editing = True

            search_paused.clear()

            entry = CTkEntry(result_frame, font=("Arial", 20), width=100)
            entry.insert(0, str(value))
            entry.grid(row=row, column=idx, sticky="nsew", padx=5, pady=5)

            def confirm_update():
                nonlocal editing
                new_value = entry.get()
                update_item(field, item_name, new_value)
                editing = False

                search_paused.set()

            confirm_button = CTkButton(
                result_frame,
                text="Güncelle",
                command=confirm_update,
                font=("Arial", 12),
                width=30,
            )
            confirm_button.grid(row=row, column=idx + 1, sticky="nsew", padx=5, pady=5)

            label_widget.destroy()

        def on_label_click(event, field, value, idx, item_name, row):
            label_widget = event.widget
            make_entry(event, field, value, idx, label_widget, item_name, row)

        def create_widgets():
            global row_index, items_per_page, current_page, update_scheduled

            start_idx = current_page * items_per_page
            end_idx = start_idx + items_per_page

            for (
                match_position,
                item_barcode,
                item_name,
                item_stock,
                item_price,
            ) in matched_items[start_idx:end_idx]:
                barcode_label = CTkLabel(
                    result_frame,
                    text=item_barcode,
                    anchor="w",
                    padx=5,
                    font=("Arial", 18),
                )
                barcode_label.grid(
                    row=row_index, column=0, sticky="nsew", padx=5, pady=5
                )
                barcode_label.bind(
                    "<Button-1>",
                    lambda e, field="barcode", value=item_barcode, row=row_index, item_name=item_name: on_label_click(
                        e, field, value, 0, item_name, row
                    ),
                )

                name_label = CTkLabel(
                    result_frame,
                    text=item_name,
                    anchor="w",
                    padx=5,
                    font=("Arial", 18),
                )
                name_label.grid(row=row_index, column=1, sticky="nsew", padx=5, pady=5)
                name_label.bind(
                    "<Button-1>",
                    lambda e, field="name", value=item_name, row=row_index, item_name=item_name: on_label_click(
                        e, field, value, 1, item_name, row
                    ),
                )

                stock_label = CTkLabel(
                    result_frame,
                    text=item_stock,
                    anchor="w",
                    padx=5,
                    font=("Arial", 18)
                )
                stock_label.grid(row=row_index, column=2, sticky="nsew", padx=5, pady=5)
                stock_label.bind(
                    "<Button-1>",
                    lambda e, field="stock", value=item_stock, row=row_index, item_name=item_name: on_label_click(
                        e, field, value, 2, item_name, row
                    ),
                )

                try:
                    item_price = float(item_price)
                except ValueError:
                    item_price = 0.0

                price_label = CTkLabel(
                    result_frame,
                    text=f"{item_price:.2f}₺",
                    anchor="w",
                    padx=5,
                    font=("Arial", 18),
                )
                price_label.grid(row=row_index, column=3, sticky="nsew", padx=5, pady=5)
                price_label.bind(
                    "<Button-1>",
                    lambda e, field="price", value=item_price, row=row_index, item_name=item_name: on_label_click(
                        e, field, value, 3, item_name, row
                    ),
                )

                add_button = CTkButton(
                    result_frame,
                    text="+",
                    font=("Arial", 18),
                    width=40,
                    command=lambda name=item_name: add_to_basket(name),
                )
                add_button.grid(row=row_index, column=4, sticky="nsew", padx=5, pady=5)

                row_index += 1
                current_page += 1

        update_scheduled = False
        loading = False
        ui_queue.put(create_widgets)

    if search_thread and not search_thread.done():
        search_cancelled = True
        search_thread.cancel()

    search_cancelled = False
    search_paused.set()
    search_thread = executor.submit(searching)

    def _on_mouse_wheel(event):
        global update_scheduled, items_per_page
        scroll_direction = int(-1 * (event.delta / 120))

        x_mouse = app.winfo_pointerx()
        screen_width = app.winfo_screenwidth()
        half_screen = (screen_width / 2) + 400

        if x_mouse < half_screen:
            search_canvas.yview_scroll(scroll_direction, "units")
        else:
            basket_canvas.yview_scroll(scroll_direction, "units")

        if not loading and search_canvas.yview()[1] >= 0.99 and not update_scheduled:
            update_scheduled = True
            items_per_page = 1
            threading.Thread(target=ui_queue.put(update_widgets)).start()

    app.bind_all("<MouseWheel>", _on_mouse_wheel)


def update_item(field, item_name, new_value):
    search_paused.clear()

    if field == "barcode":
        storage.update_item_barcode(item_name, new_value)
    elif field == "name":
        storage.update_item_name(item_name, new_value)
    elif field == "price":
        try:
            new_value = float(new_value)
        except ValueError:
            new_value = 0.0
        storage.update_item_price(item_name, new_value)
    elif field == "stock":
        try:
            new_value = int(new_value)
        except ValueError:
            new_value = 0
        storage.update_item_stock(item_name, new_value)

    search_paused.set()

    search_items()


def open_add_product_window():
    search_paused.clear()

    add_product_window = CTkToplevel(app)
    add_product_window.title("Ürün Ekle")
    add_product_window.geometry("500x300")
    add_product_window.grab_set()

    barcode_frame = CTkFrame(add_product_window)
    barcode_frame.pack(fill="both", expand=True, padx=5, pady=(5, 5))

    barcode_label = CTkLabel(barcode_frame, text="Barcod:", font=("Arial", 22))
    barcode_label.pack(side="left", padx=5)
    barcode_entry = CTkEntry(barcode_frame, font=("Arial", 22), width=350)
    barcode_entry.pack(side="right", padx=5)

    name_frame = CTkFrame(add_product_window)
    name_frame.pack(fill="both", expand=True, padx=5, pady=(5, 5))

    name_label = CTkLabel(name_frame, text="İsim:", font=("Arial", 22))
    name_label.pack(side="left", padx=5)
    name_entry = CTkEntry(name_frame, font=("Arial", 22), width=350)
    name_entry.pack(side="right", padx=5)

    price_frame = CTkFrame(add_product_window)
    price_frame.pack(fill="both", expand=True, padx=5, pady=(5, 5))

    price_label = CTkLabel(price_frame, text="Fiyat:", font=("Arial", 22))
    price_label.pack(side="left", padx=5)
    price_entry = CTkEntry(price_frame, font=("Arial", 22), width=350)
    price_entry.pack(side="right", padx=5)

    stock_frame = CTkFrame(add_product_window)
    stock_frame.pack(fill="both", expand=True, padx=5, pady=(5, 5))

    stock_label = CTkLabel(stock_frame, text="Stok:", font=("Arial", 22))
    stock_label.pack(side="left", padx=5)
    stock_entry = CTkEntry(stock_frame, font=("Arial", 22), width=350)
    stock_entry.pack(side="right", padx=5)

    def add_product():
        try:
            barcode = barcode_entry.get()
            name = name_entry.get()
            price = float(price_entry.get())
            stock = int(stock_entry.get())

            code39_charset = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+%* ")

            if not barcode:
                warning_label.configure(text="Barcod alanı boş olamaz.")
                return
            for char in barcode:
                if char not in code39_charset:
                    warning_label.configure(
                        text=f"Barkodda geçersiz karakter: '{char}'"
                    )
                    return
            if not name:
                warning_label.configure(text="İsim alanı boş olamaz.")
                return
            if not price:
                warning_label.configure(text="Fiyat alanı boş olamaz.")
                return
            if not stock:
                warning_label.configure(text="Stok alanı boş olamaz.")
                return

            if storage.barcode_exists(barcode):
                warning_label.configure(text="Bu barkod zaten depoda mevcut.")
            elif storage.item_exists(name):
                warning_label.configure(text="Bu ürün ismi zaten depoda mevcut.")
            else:
                storage.add_product(barcode, name, price, stock)
                add_product_window.destroy()
                search_items()
        except ValueError:
            warning_label.configure(
                text="Geçersiz değerler girdiniz. Lütfen tekrar deneyin."
            )

    warning_label = CTkLabel(
        add_product_window, text="", font=("Arial", 16), text_color="red"
    )
    warning_label.pack(pady=(0, 0))

    add_button = CTkButton(
        add_product_window,
        text="Ürünlere Ekle",
        command=add_product,
        font=("Arial", 22, "bold"),
    )
    add_button.pack(pady=(0, 10))
    search_paused.set()


search_bar.bind("<KeyRelease>", search_items)


def confirm_order():
    for item in basket.get_basket_items():
        storage.reduce_stock(item["name"], item["amount"])
    basket.clear_basket()
    update_basket_display()
    search_items()


search_items()
app.mainloop()
