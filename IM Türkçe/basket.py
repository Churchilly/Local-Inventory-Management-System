# basket.py
import os
from fpdf import FPDF
import json

basket = []
total_value = 0.0
PRINT_ORDER_FILE = "assets/print_order.json"


def init_json():
    if not os.path.exists(PRINT_ORDER_FILE):
        with open(PRINT_ORDER_FILE, "w") as file:
            json.dump({"order_number": 0}, file)


def get_current_print_order():
    with open(PRINT_ORDER_FILE, "r") as file:
        data = json.load(file)
        return data["order_number"]


def update_print_order(new_order):
    with open(PRINT_ORDER_FILE, "w") as file:
        json.dump({"order_number": new_order}, file)


init_json()


def add_to_basket(item_name, item_price):
    global total_value
    for item in basket:
        if item["name"] == item_name:
            item["amount"] += 1
            break
    else:
        basket.append({"name": item_name, "price": item_price, "amount": 1})
    total_value = sum(item["price"] * item["amount"] for item in basket)


def remove_from_basket(item_name):
    global basket, total_value
    basket = [item for item in basket if item["name"] != item_name]
    total_value = sum(item["price"] * item["amount"] for item in basket)


def update_item_amount(item_name, amount):
    global total_value
    for item in basket:
        if item["name"] == item_name:
            item["amount"] = amount
            break
    total_value = sum(item["price"] * item["amount"] for item in basket)


def get_total_value():
    return total_value


def get_basket_items():
    return basket


def clear_basket():
    global basket, total_value
    basket = []
    total_value = 0.0


def print_basket():
    pdf = FPDF()
    pdf.add_page()

    font_path_dejavu = os.path.join(
        os.path.dirname(__file__), "assets/Fonts", "DejaVuSans.ttf"
    )
    pdf.add_font("DejaVu", "", font_path_dejavu, uni=True)
    pdf.set_font("DejaVu", size=12)

    font_path_dejavub = os.path.join(
        os.path.dirname(__file__), "assets/Fonts", "DejaVuSans-Bold.ttf"
    )
    pdf.add_font("DejaVu", "B", font_path_dejavub, uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.set_font("DejaVu", size=16, style="B")
    pdf.cell(200, 10, txt="Sipariş Teklifi", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("DejaVu", size=12)
    pdf.cell(110, 10, txt="Ürün Adı", border=1, align="C")
    pdf.cell(30, 10, txt="Birim Fiyat", border=1, align="C")
    pdf.cell(20, 10, txt="Miktar", border=1, align="C")
    pdf.cell(30, 10, txt="Toplam Fiyat", border=1, align="C")
    pdf.ln(10)

    for item in basket:
        pdf.cell(110, 10, txt=item["name"], border=1)
        pdf.cell(30, 10, txt=f"{item['price']:.2f}₺", border=1, align="C")
        pdf.cell(20, 10, txt=str(item["amount"]), border=1, align="C")
        pdf.cell(
            30, 10, txt=f"{item['price'] * item['amount']:.2f}₺", border=1, align="C"
        )
        pdf.ln(10)

    pdf.ln(10)
    pdf.cell(110, 10, border=0)
    pdf.cell(50, 10, txt="Toplam", border=1, align="C")
    pdf.cell(30, 10, txt=f"{get_total_value():.2f}₺", border=1, align="C")
    pdf.ln(10)

    order_number = get_current_print_order() + 1
    update_print_order(order_number)

    directory = os.path.join(os.path.dirname(__file__), "Teklifler")
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = f"teklif-{order_number}.pdf"
    filepath = os.path.join(directory, filename)
    pdf.output(filepath)

    try:
        os.startfile(filepath)
    except Exception as e:
        pass
