from random import weibullvariate
import flet as ft
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import json
import subprocess
import os
import re
import time

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='agos_pos',
            user='root',
            password=''
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_database():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS agos_pos")
        cursor.execute("USE agos_pos")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(100) NOT NULL,
                stock INT DEFAULT 0,
                img VARCHAR(500)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                subtotal DECIMAL(10,2) NOT NULL,
                discount DECIMAL(10,2) NOT NULL,
                fees DECIMAL(10,2) NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                cash DECIMAL(10,2) NOT NULL,
                change_amount DECIMAL(10,2) NOT NULL,
                items JSON NOT NULL,
                timestamp DATETIME NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                sukiCard VARCHAR(9)
            )
        """)

        cursor.execute("SHOW COLUMNS FROM transactions LIKE 'payment_method'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE transactions ADD COLUMN payment_method VARCHAR(50) NOT NULL")

        cursor.execute("SHOW COLUMNS FROM transactions LIKE 'sukiCard'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE transactions ADD COLUMN sukiCard VARCHAR(9)")

        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ("Laptop Gaming", 10000, "Laptop", 15, "https://cdn-icons-png.flaticon.com/512/6742/6742591.png"),
                ("Drone Mavic Pro", 9999, "Drone", 8, "https://cdn-icons-png.flaticon.com/512/10608/10608591.png"),
                ("Canon Camera", 6999, "Camera", 12, "https://cdn-icons-png.flaticon.com/512/685/685655.png"),
                ("Iphone X - Black", 3499, "Phone", 25,
                 "https://clearscopetech.com/wp-content/uploads/2023/11/smartphone_2482945-300x300.png"),
                ("Logitech Keyboard", 2999, "Accessories", 30,
                 "https://static.vecteezy.com/system/resources/previews/037/233/013/non_2x/keyword-blue-filled-icon-vector.jpg"),
                ("Acer Monitor", 2000, "Monitor", 10,
                 "https://static.vecteezy.com/system/resources/previews/013/279/623/large_2x/illustration-icon-of-a-modern-digital-digital-smart-rectangular-computer-with-monitor-laptop-isolated-on-white-background-concept-computer-digital-technologies-free-vector.jpg"),
                ("Ipad Gen-6", 9999, "Tablet", 7,
                 "https://static.vecteezy.com/system/resources/previews/035/886/963/non_2x/office-tools-tablet-object-illustration-vector.jpg"),
                ("Razer Mamba Mouse", 1499, "Mouse", 20, "https://cdn-icons-png.flaticon.com/512/815/815740.png"),
                ("Logitech G Pro Wireless", 899, "Mouse", 18, "https://cdn-icons-png.flaticon.com/512/815/815740.png"),
                ("ROG Strix GL504GV", 12999, "Laptop", 5, "https://cdn-icons-png.flaticon.com/512/6742/6742591.png"),
                ("Samsung Monitor", 1799, "Monitor", 9,
                 "https://static.vecteezy.com/system/resources/previews/013/279/623/large_2x/illustration-icon-of-a-modern-digital-digital-smart-rectangular-computer-with-monitor-laptop-isolated-on-white-background-concept-computer-digital-technologies-free-vector.jpg"),
                ("ROG Phone", 4399, "Phone", 15,
                 "https://clearscopetech.com/wp-content/uploads/2023/11/smartphone_2482945-300x300.png"),
                ("Samsung Galaxy S21", 6399, "Phone", 20,
                 "https://clearscopetech.com/wp-content/uploads/2023/11/smartphone_2482945-300x300.png"),
                ("MacBook Air M2", 8399, "Laptop", 12, "https://cdn-icons-png.flaticon.com/512/6742/6742591.png"),
                ("iPad Pro 12.9", 11999, "Tablet", 6,
                 "https://static.vecteezy.com/system/resources/previews/035/886/963/non_2x/office-tools-tablet-object-illustration-vector.jpg"),
                ("Nikon DSLR", 5999, "Camera", 8, "https://cdn-icons-png.flaticon.com/512/685/685655.png"),
                ("Logitech MX Master Mouse", 999, "Mouse", 25, "https://cdn-icons-png.flaticon.com/512/815/815740.png"),
                ("Dell UltraSharp Monitor", 2799, "Monitor", 4,
                 "https://static.vecteezy.com/system/resources/previews/013/279/623/large_2x/illustration-icon-of-a-modern-digital-digital-smart-rectangular-computer-with-monitor-laptop-isolated-on-white-background-concept-computer-digital-technologies-free-vector.jpg"),
                ("Wireless Earbuds Pro", 1999, "Accessories", 35,
                 "https://cdn-icons-png.flaticon.com/512/566/566299.png"),
                ("DJI Mini Drone", 4699, "Drone", 10, "https://cdn-icons-png.flaticon.com/512/10608/10608591.png"),
                ("Sony A7 Camera", 19999, "Camera", 3, "https://cdn-icons-png.flaticon.com/512/685/685655.png"),
                ("Samsung Galaxy Tab S8", 11099, "Tablet", 9,
                 "https://static.vecteezy.com/system/resources/previews/035/886/963/non_2x/office-tools-tablet-object-illustration-vector.jpg"),
                ("HP Pavilion Laptop", 8999, "Laptop", 18, "https://cdn-icons-png.flaticon.com/512/6742/6742591.png"),
                ("Apple Magic Keyboard", 1099, "Accessories", 22,
                 "https://static.vecteezy.com/system/resources/previews/037/233/013/non_2x/keyword-blue-filled-icon-vector.jpg"),
                ("Google Pixel 7", 9399, "Phone", 28,
                 "https://clearscopetech.com/wp-content/uploads/2023/11/smartphone_2482945-300x300.png"),
                ("Lenovo ThinkPad X1", 15999, "Laptop", 8, "https://cdn-icons-png.flaticon.com/512/6742/6742591.png"),
                ("MSI Gaming Laptop", 18999, "Laptop", 6, "https://cdn-icons-png.flaticon.com/512/6742/6742591.png"),
                ("Dell Inspiron 15", 7599, "Laptop", 14, "https://cdn-icons-png.flaticon.com/512/6742/6742591.png"),
                ("DJI Phantom 4", 12999, "Drone", 5, "https://cdn-icons-png.flaticon.com/512/10608/10608591.png"),
                ("Holy Stone HS720", 3999, "Drone", 12, "https://cdn-icons-png.flaticon.com/512/10608/10608591.png"),
                ("Autel Robotics EVO", 15999, "Drone", 3, "https://cdn-icons-png.flaticon.com/512/10608/10608591.png"),
                ("Sony Cyber-shot RX100", 8999, "Camera", 10, "https://cdn-icons-png.flaticon.com/512/685/685655.png"),
                ("Fujifilm X-T30", 12999, "Camera", 7, "https://cdn-icons-png.flaticon.com/512/685/685655.png"),
                ("Olympus OM-D E-M10", 6999, "Camera", 9, "https://cdn-icons-png.flaticon.com/512/685/685655.png"),
                ("OnePlus 11", 8599, "Phone", 18,
                 "https://clearscopetech.com/wp-content/uploads/2023/11/smartphone_2482945-300x300.png"),
                ("Xiaomi 13 Pro", 7999, "Phone", 22,
                 "https://clearscopetech.com/wp-content/uploads/2023/11/smartphone_2482945-300x300.png"),
                ("Nothing Phone 2", 6999, "Phone", 15,
                 "https://clearscopetech.com/wp-content/uploads/2023/11/smartphone_2482945-300x300.png"),
                (
                    "Anker Power Bank", 1299, "Accessories", 40,
                    "https://cdn-icons-png.flaticon.com/512/3098/3098524.png"),
                ("Samsung Smart Watch", 4999, "Accessories", 16,
                 "https://i.pinimg.com/736x/aa/e1/5c/aae15c67c8dd1e82b6509b4624952af1.jpg"),
                ("JBL Bluetooth Speaker", 2499, "Accessories", 25,
                 "https://cdn.icon-icons.com/icons2/933/PNG/512/filled-speaker-with-white-details_icon-icons.com_72755.png"),
                ("LG UltraGear 27\"", 8999, "Monitor", 7,
                 "https://static.vecteezy.com/system/resources/previews/013/279/623/large_2x/illustration-icon-of-a-modern-digital-digital-smart-rectangular-computer-with-monitor-laptop-isolated-on-white-background-concept-computer-digital-technologies-free-vector.jpg"),
                ("ASUS ProArt Display", 12999, "Monitor", 4,
                 "https://static.vecteezy.com/system/resources/previews/013/279/623/large_2x/illustration-icon-of-a-modern-digital-digital-smart-rectangular-computer-with-monitor-laptop-isolated-on-white-background-concept-computer-digital-technologies-free-vector.jpg"),
                ("AOC Gaming Monitor", 5999, "Monitor", 11,
                 "https://static.vecteezy.com/system/resources/previews/013/279/623/large_2x/illustration-icon-of-a-modern-digital-digital-smart-rectangular-computer-with-monitor-laptop-isolated-on-white-background-concept-computer-digital-technologies-free-vector.jpg"),
                ("Microsoft Surface Pro", 13999, "Tablet", 8,
                 "https://static.vecteezy.com/system/resources/previews/035/886/963/non_2x/office-tools-tablet-object-illustration-vector.jpg"),
                ("Lenovo Tab P12", 8999, "Tablet", 12,
                 "https://static.vecteezy.com/system/resources/previews/035/886/963/non_2x/office-tools-tablet-object-illustration-vector.jpg"),
                ("Huawei MatePad Pro", 10999, "Tablet", 10,
                 "https://static.vecteezy.com/system/resources/previews/035/886/963/non_2x/office-tools-tablet-object-illustration-vector.jpg"),
                ("SteelSeries Rival 3", 1599, "Mouse", 20, "https://cdn-icons-png.flaticon.com/512/815/815740.png"),
                ("Corsair Dark Core", 2999, "Mouse", 14, "https://cdn-icons-png.flaticon.com/512/815/815740.png"),
                ("HyperX Pulsefire", 1999, "Mouse", 18, "https://cdn-icons-png.flaticon.com/512/815/815740.png"),
                ("Medusa (Dr. Stone)", 1000000, "Accessories", 20,
                 "https://www.nikkoindustries.com/cdn/shop/files/Image-Render.004_29947626-7e61-4292-8abb-03fc7b3ec0dc_700x700.png?v=1737814064"),
                ("Revival Fluid (Dr. Stone)", 10000, "Accessories", 20,
                 "https://cdn-icons-png.flaticon.com/512/8331/8331206.png")
            ]
            insert_query = "INSERT INTO products (name, price, category, stock, img) VALUES (%s, %s, %s, %s, %s)"
            cursor.executemany(insert_query, sample_products)
            connection.commit()

        cursor.close()
        connection.close()


def load_products_from_db(filter_text="", category="All"):
    connection = get_db_connection()
    if not connection:
        return []
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    if category != "All":
        query += " AND category = %s"
        params.append(category)
    if filter_text:
        query += " AND name LIKE %s"
        params.append(f"%{filter_text}%")
    cursor.execute(query, params)
    products = cursor.fetchall()
    for product in products:
        product['price'] = float(product['price'])
    cursor.close()
    connection.close()
    return products


def save_transaction_to_db(subtotal, discount, fees, total, cash, change, items, timestamp, payment_method, sukiCard):
    connection = get_db_connection()
    if not connection:
        return
    cursor = connection.cursor()
    items_json = json.dumps([{"product_id": item["product"]["id"], "name": item["product"]["name"],
                              "quantity": item["quantity"], "price": item["product"]["price"]} for item in items])
    query = """
        INSERT INTO transactions (subtotal, discount, fees, total, cash, change_amount, items, timestamp, payment_method, sukiCard)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query,
                   (subtotal, discount, fees, total, cash, change, items_json, timestamp, payment_method, sukiCard))
    connection.commit()
    cursor.close()
    connection.close()


def load_transactions_from_db():
    connection = get_db_connection()
    if not connection:
        return []
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM transactions ORDER BY timestamp DESC"
    cursor.execute(query)
    transactions = cursor.fetchall()
    for transaction in transactions:
        transaction['subtotal'] = float(transaction['subtotal'])
        transaction['discount'] = float(transaction['discount'])
        transaction['fees'] = float(transaction['fees'])
        transaction['total'] = float(transaction['total'])
        transaction['cash'] = float(transaction['cash'])
        transaction['change_amount'] = float(transaction['change_amount'])
        transaction['items'] = json.loads(transaction['items'])
    cursor.close()
    connection.close()
    return transactions


def update_stock_in_db(product_id, change):
    connection = get_db_connection()
    if not connection:
        return
    cursor = connection.cursor()
    query = "UPDATE products SET stock = GREATEST(0, stock + %s) WHERE id = %s"
    cursor.execute(query, (change, product_id))
    connection.commit()
    cursor.close()
    connection.close()


def generate_text_receipt(transaction_data):
    try:
        receipts_dir = "receipts"
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)

        timestamp = transaction_data['timestamp'].strftime("%Y%m%d_%H%M%S")
        filename = f"{receipts_dir}/receipt_{timestamp}.txt"

        receipt_content = []
        receipt_content.append("=" * 50)
        receipt_content.append("           AGOS POINT OF SALE")
        receipt_content.append("=" * 50)
        receipt_content.append(f"Date: {transaction_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        if transaction_data['sukiCard']:
            receipt_content.append(f"SukiCard: {transaction_data['sukiCard']}")
        receipt_content.append("-" * 50)
        receipt_content.append("ITEMS:")
        receipt_content.append("-" * 50)

        for item in transaction_data['items']:
            item_total = item['product']['price'] * item['quantity']
            receipt_content.append(f"{item['product']['name']:<30} x{item['quantity']:<3} ₱{item_total:>8.2f}")

        receipt_content.append("-" * 50)
        receipt_content.append(f"Subtotal:               ₱{transaction_data['subtotal']:>8.2f}")

        if transaction_data['discount'] > 0:
            receipt_content.append(f"Discount (20%):         -₱{transaction_data['discount']:>8.2f}")

        receipt_content.append(f"Fees:                   ₱{transaction_data['fees']:>8.2f}")
        receipt_content.append("-" * 50)
        receipt_content.append(f"TOTAL:                  ₱{transaction_data['total']:>8.2f}")
        receipt_content.append(f"Payment Method:         {transaction_data['payment_method']}")
        receipt_content.append(f"Paid:                   ₱{transaction_data['cash']:>8.2f}")
        receipt_content.append(f"Change:                 ₱{transaction_data['change']:>8.2f}")
        receipt_content.append("=" * 50)
        receipt_content.append("      THANK YOU FOR YOUR PURCHASE!")
        receipt_content.append("=" * 50)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(receipt_content))

        return filename
    except Exception as e:
        print(f"Error generating receipt file: {e}")
        return None


def main(page: ft.Page):
    init_database()
    page.title = "Agos POS"
    page.scroll = "adaptive"
    page.bgcolor = "#E6F7FA"
    page.window.maximized = True

    cart = []
    receipt_data = None
    current_category = "All"

    receipt_items = ft.Column()
    receipt_subtotal = ft.Text("", color="#0077b6")
    receipt_discount = ft.Text("", color="#0077b6")
    receipt_fees = ft.Text("", color="#0096c7")
    receipt_total = ft.Text("", size=18, weight="bold", color="#03045e")
    receipt_payment_method = ft.Text("", color="#0077b6")
    receipt_paid = ft.Text("", color="#0077b6")
    receipt_change = ft.Text("", weight="bold", color="#008000")
    receipt_timestamp = ft.Text("", size=12, color="grey")
    receipt_sukiCard = ft.Text("", color="#0077b6")

    receipt_overlay = ft.Container(
        visible=False,
        expand=True,
        bgcolor=ft.Colors.BLACK54,
        alignment=ft.alignment.center,
        content=ft.Container(
            width=500,
            height=600,
            bgcolor="white",
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color="#000000"),
            padding=30,
            content=ft.Column([
                ft.Text("Transaction Receipt", size=20, weight="bold", color="#023e8a"),
                ft.Divider(),
                receipt_timestamp,
                receipt_sukiCard,
                ft.Divider(),
                receipt_items,
                ft.Divider(),
                receipt_subtotal,
                receipt_discount,
                receipt_fees,
                receipt_total,
                receipt_payment_method,
                receipt_paid,
                receipt_change,
                ft.Divider(),
                ft.ElevatedButton("Save Receipt", bgcolor="#00B4D8", color="white",
                                  on_click=lambda e: save_receipt_file(e)),
                ft.ElevatedButton("Close", bgcolor="#0096c7", color="white", on_click=lambda e: hide_receipt(e)),
            ], scroll="adaptive")
        )
    )

    def save_receipt_file(e):
        if receipt_data:
            filename = generate_text_receipt(receipt_data)
            if filename:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"✅ Receipt saved as: {filename}"),
                    bgcolor="green"
                )
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text("❌ Error saving receipt file"),
                    bgcolor="red"
                )
            page.snack_bar.open = True
            page.update()

    search_box = ft.TextField(
        hint_text="Search here...",
        width=250,
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        border_color="#00B4D8"
    )

    header = ft.Row([
        ft.Row(
            controls=[
                ft.Image(
                    src="https://scontent.ftdg1-1.fna.fbcdn.net/v/t1.15752-9/557422905_1543372830163868_8222908200224575867_n.png?_nc_cat=101&ccb=1-7&_nc_sid=9f807c&_nc_eui2=AeGWb91tM_aT3G0ZjpMBfNcPgJyGdF3KuO6AnIZ0Xcq47hEEATh6Iz7uj3kodUkG4o5HgjzIhsFRtwvI9OOq6vsT&_nc_ohc=pAxyhkoDeAsQ7kNvwFqfulF&_nc_oc=Adm-6nSxxZ_LpnXv4Er83nRR-JXs2PbgItzypQVmgAB2rVVA3kUY36IoYTWyY9si-Z4&_nc_zt=23&_nc_ht=scontent.ftdg1-1.fna&oh=03_Q7cD3gFT59hNmoyxLBT9LUqoFrsK0_sAdF3HxVnXW4f-HU12Hw&oe=6907EA05&dl=1",
                    width=100,
                    height=100,
                    fit="contain",
                    border_radius=40,
                )
            ]
        ),
        ft.Text("Agos Point of Sale", size=30, weight="bold", color="#023e8a"),
        ft.Container(expand=True),
        search_box,
        ft.IconButton(ft.Icons.FILTER_ALT, icon_color="#0096c7")
    ], alignment="spaceBetween")

    cart_list = ft.Column(scroll="adaptive", height=300)
    subtotal = ft.Text("Subtotal: ₱0", color="#0077b6", weight="bold")
    fees = ft.Text("Fees: ₱20", color="#0096c7", weight="bold")
    discount_label = ft.Text("Discount (0%): -₱0.00", color="#0077b6", weight="bold")
    total = ft.Text("Total: ₱20", weight="bold", size=18, color="#03045e")
    change_display = ft.Text("Change: ₱0.00", weight="bold", color="#008000")
    discount_checkbox = ft.Checkbox(
        label="Senior Citizen / PWD (20% off)",
        value=False,
        hover_color="BLUE"
    )
    cash_input = ft.TextField(
        label="Enter cash amount (₱)",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        color="BLACK",
        border_color="BLUE",
        border_radius=10,
        on_change=lambda e: calculate_change()
    )

    def suki_card_changed(e):
        update_cart()
        calculate_change()

    sukiCard_input = ft.TextField(
        label="SukiCard Number (9 digits, optional)",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        color="BLACK",
        border_color="BLUE",
        border_radius=10,
        on_change=suki_card_changed
    )
    insufficient_cash = ft.Text("", color="red", visible=False)

    grid = ft.GridView(expand=True, runs_count=4, spacing=10, run_spacing=10)

    cart_section = ft.Container(
        width=350,
        bgcolor="white",
        padding=15,
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=8, color="#00B4D8"),
        content=ft.Column([
            ft.Text("🛒 Detail Items", size=20, weight="bold", color="#03045e"),
            ft.Divider(),
            ft.Container(
                content=cart_list,
                expand=True,
                height=300,
                bgcolor="#f0f8ff",
                border_radius=10,
                padding=5,
            ),
            ft.Divider(thickness=10, color="#00B4D8"),
            subtotal,
            discount_label,
            fees,
            total,
            discount_checkbox,
            cash_input,
            sukiCard_input,
            change_display,
            insufficient_cash,
            ft.Row([
                ft.ElevatedButton("Pay Now", expand=True, bgcolor="#00B4D8", color="white",
                                  on_click=lambda e: pay_now(e)),
                ft.OutlinedButton("Cancel", expand=True, style=ft.ButtonStyle(color={"": "#0096c7"}),
                                  on_click=lambda e: clear_cart(e))
            ])
        ])
    )

    def calculate_change():
        try:
            cash = float(cash_input.value or 0)
        except ValueError:
            cash = 0

        subtotal_val = sum(item['product']['price'] * item['quantity'] for item in cart)
        discount_rate = 0.2 if discount_checkbox.value else 0
        discount_val = subtotal_val * discount_rate
        discounted_subtotal = subtotal_val - discount_val

        suki_card = sukiCard_input.value.strip()
        fees_val = 0.0 if re.match(r'^\d{9}$', suki_card) else 20.0
        total_val = discounted_subtotal + fees_val

        change = cash - total_val

        if cash > 0:
            if change >= 0:
                change_display.value = f"Change: ₱{change:.2f}"
                change_display.color = "#008000"
                insufficient_cash.visible = False
            else:
                change_display.value = f"Additional: ₱{-change:.2f}"
                change_display.color = "red"
                insufficient_cash.value = "Insufficient cash!"
                insufficient_cash.visible = True
        else:
            change_display.value = "Change: ₱0.00"
            change_display.color = "#008000"
            insufficient_cash.visible = False

        page.update()

    login_error_message = ft.Text(
        "",
        color="red",
        size=14,
        weight="bold",
        text_align="center",
        visible=False
    )

    def reset_login_state():
        username_field.value = ""
        password_field.value = ""
        login_button.text = "Login"
        login_button.disabled = False
        login_error_message.visible = False
        page.update()

    def login_clicked(e):
        login_button.text = "Checking..."
        login_button.disabled = True
        login_error_message.visible = False
        page.update()

        time.sleep(0.5)

        if username_field.value == "admin" and password_field.value == "admin":
            reset_login_state()
            page.go("/main")
        else:
            login_error_message.value = "❌ Invalid credentials!"
            login_error_message.visible = True
            password_field.value = ""
            login_button.text = "Login"
            login_button.disabled = False
            page.update()

    def create_sidebar(current_tab):
        selected_bg = "#023e8a"
        unselected_bg = "transparent"
        icon_color = "white"

        home_container = ft.Container(
            bgcolor=selected_bg if current_tab == "home" else unselected_bg,
            border_radius=8,
            padding=4,
            content=ft.IconButton(
                icon=ft.Icons.HOME,
                icon_color=icon_color,
                tooltip="Home",
                on_click=lambda e: page.go("/main")
            )
        )

        stock_container = ft.Container(
            bgcolor=selected_bg if current_tab == "stock" else unselected_bg,
            border_radius=8,
            padding=4,
            content=ft.IconButton(
                icon=ft.Icons.INVENTORY_2,
                icon_color=icon_color,
                tooltip="Stock Management",
                on_click=lambda e: page.go("/stock")
            )
        )

        stats_container = ft.Container(
            bgcolor=selected_bg if current_tab == "statistics" else unselected_bg,
            border_radius=8,
            padding=4,
            content=ft.IconButton(
                icon=ft.Icons.BAR_CHART,
                icon_color=icon_color,
                tooltip="Statistics",
                on_click=lambda e: page.go("/statistics")
            )
        )

        logout_container = ft.Container(
            bgcolor=unselected_bg,
            border_radius=8,
            padding=4,
            content=ft.IconButton(
                icon=ft.Icons.LOGOUT,
                icon_color=icon_color,
                tooltip="Logout",
                on_click=lambda e: logout_app(e)
            )
        )

        return ft.Container(
            width=65,
            bgcolor="#0096c7",
            padding=5,
            border_radius=10,
            content=ft.Column([
                home_container,
                stock_container,
                stats_container,
                logout_container,
            ], spacing=20, alignment="center")
        )

    def update_cart():
        cart_list.controls.clear()
        subtotal_val = sum(item['product']['price'] * item['quantity'] for item in cart)
        discount_rate = 0.2 if discount_checkbox.value else 0
        discount_val = subtotal_val * discount_rate
        discounted_subtotal = subtotal_val - discount_val

        suki_card = sukiCard_input.value.strip()
        fees_val = 0.0 if re.match(r'^\d{9}$', suki_card) else 20.0
        total_val = discounted_subtotal + fees_val

        for index, item in enumerate(cart):
            cart_list.controls.append(
                ft.Row([
                    ft.Image(src=item["product"]["img"], width=40, height=40),
                    ft.Column([
                        ft.Text(f"{item['product']['name']}", weight="bold", size=14, color="BLACK"),
                        ft.Text(
                            f"₱{item['product']['price']} x {item['quantity']} = ₱{item['product']['price'] * item['quantity']:.2f}",
                            size=12, color="grey"),
                    ], expand=True),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.REMOVE,
                            icon_size=16,
                            tooltip="Remove one",
                            on_click=lambda e, idx=index: remove_from_cart(idx, 1)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_size=16,
                            icon_color="red",
                            tooltip="Remove all",
                            on_click=lambda e, idx=index: remove_from_cart(idx, item['quantity'])
                        ),
                        ft.TextField(
                            value="1",
                            width=50,
                            height=30,
                            color="black",
                            text_size=12,
                            text_align="center",
                            keyboard_type=ft.KeyboardType.NUMBER,
                            on_submit=lambda e, idx=index: remove_specific_quantity(idx, e.control.value)
                        ),
                    ], spacing=2)
                ], alignment="center", vertical_alignment="center")
            )
        subtotal.value = f"Subtotal: ₱{subtotal_val:.2f}"
        fees.value = f"Fees: ₱{fees_val:.2f}"
        discount_label.value = f"Discount ({'20%' if discount_checkbox.value else '0%'}): -₱{discount_val:.2f}"
        total.value = f"Total: ₱{total_val:.2f}"
        calculate_change()
        page.update()

    def remove_from_cart(index, quantity_to_remove):
        if 0 <= index < len(cart):
            item = cart[index]
            prod = item['product']
            if quantity_to_remove >= item['quantity']:
                add_back = item['quantity']
                cart.pop(index)
            else:
                item['quantity'] -= quantity_to_remove
                add_back = quantity_to_remove
            prod['stock'] += add_back
            update_stock_in_db(prod['id'], add_back)
        update_cart()
        load_products(search_box.value, current_category)

    def remove_specific_quantity(index, quantity_str):
        try:
            quantity_to_remove = int(quantity_str)
            if quantity_to_remove <= 0:
                return
            remove_from_cart(index, quantity_to_remove)
        except ValueError:
            pass

    def clear_cart(e):
        for item in cart:
            item['product']['stock'] += item['quantity']
            update_stock_in_db(item['product']['id'], item['quantity'])
        cart.clear()
        update_cart()
        load_products(search_box.value, current_category)

    def discount_changed(e):
        update_cart()
        calculate_change()

    def exit_app(e):
        page.window.close()

    def logout_app(e):
        clear_cart(None)
        reset_login_state()
        page.go("/")

    def adjust_stock(e, product, is_add=True):
        try:
            qty = int(e.control.value)
            if qty < 0:
                qty = 0
            change = qty if is_add else -qty
            product['stock'] += change
            update_stock_in_db(product['id'], change)
            if product['stock'] < 0:
                product['stock'] = 0
            e.control.value = ""
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Stock {'added' if is_add else 'removed'} successfully!"),
                bgcolor="green"
            )
            page.snack_bar.open = True
            if page.route == "/stock":
                page.views[-1].controls.clear()
                page.views[-1].controls.append(create_stock_view().controls[0])
            page.update()
        except ValueError:
            page.snack_bar = ft.SnackBar(
                ft.Text("Invalid quantity! Please enter a number."),
                bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()

    def show_receipt():
        if receipt_data:
            update_receipt_display()
            receipt_overlay.visible = True
            page.update()

    def hide_receipt(e):
        receipt_overlay.visible = False
        page.update()

    def pay_now(e):
        try:
            cash = float(cash_input.value or 0)
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Invalid cash input!"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return

        sukiCard = sukiCard_input.value.strip()
        if sukiCard and not re.match(r'^\d{9}$', sukiCard):
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ SukiCard must be a 9-digit number!"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return

        subtotal_val = sum(item['product']['price'] * item['quantity'] for item in cart)
        discount_rate = 0.2 if discount_checkbox.value else 0
        discount_val = subtotal_val * discount_rate
        discounted_subtotal = subtotal_val - discount_val

        # Determine fees based on SukiCard status
        fees_val = 0.0 if sukiCard and re.match(r'^\d{9}$', sukiCard) else 20.0
        total_val = discounted_subtotal + fees_val
        payment_method = "Cash"

        insufficient_cash.visible = False

        if cash < total_val:
            insufficient_cash.value = "Insufficient cash!"
            insufficient_cash.visible = True
            page.update()
            return

        change = cash - total_val
        timestamp = datetime.now()
        global receipt_data
        receipt_data = {
            'items': cart.copy(),
            'subtotal': subtotal_val,
            'discount': discount_val,
            'fees': fees_val,
            'total': total_val,
            'cash': cash,
            'change': change,
            'timestamp': timestamp,
            'payment_method': payment_method,
            'sukiCard': sukiCard if sukiCard else None
        }

        save_transaction_to_db(subtotal_val, discount_val, fees_val, total_val, cash, change, cart, timestamp,
                               payment_method, sukiCard)

        receipt_filename = generate_text_receipt(receipt_data)

        show_receipt()
        cart.clear()
        update_cart()
        cash_input.value = ""
        sukiCard_input.value = ""
        discount_checkbox.value = False
        change_display.value = "Change: ₱0.00"

        if receipt_filename:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"✅ Transaction completed! Receipt saved as: {receipt_filename}"),
                bgcolor="green"
            )
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("✅ Transaction completed! (Error saving receipt file)"),
                bgcolor="orange"
            )
        page.snack_bar.open = True
        page.update()

    def update_receipt_display():
        if not receipt_data:
            return
        receipt_items.controls.clear()
        for item in receipt_data['items']:
            receipt_items.controls.append(
                ft.Row([
                    ft.Text(f"{item['product']['name']} (x{item['quantity']})", expand=True),
                    ft.Text(f"₱{item['product']['price'] * item['quantity']:.2f}")
                ])
            )
        receipt_subtotal.value = f"Subtotal: ₱{receipt_data['subtotal']:.2f}"
        receipt_discount.value = f"Discount ({'20%' if receipt_data['discount'] > 0 else '0%'}): -₱{receipt_data['discount']:.2f}"
        receipt_fees.value = f"Fees: ₱{receipt_data['fees']:.2f}"
        receipt_total.value = f"Total: ₱{receipt_data['total']:.2f}"
        receipt_payment_method.value = f"Payment Method: {receipt_data['payment_method']}"
        receipt_paid.value = f"Paid: ₱{receipt_data['cash']:.2f}"
        receipt_change.value = f"Change: ₱{receipt_data['change']:.2f}"
        receipt_timestamp.value = f"Time: {receipt_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
        receipt_sukiCard.value = f"SukiCard: {receipt_data['sukiCard'] if receipt_data['sukiCard'] else 'None'}"

    def add_to_cart(p, quantity=1):
        if quantity <= 0:
            return
        if p['stock'] < quantity:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Not enough stock!"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return
        for item in cart:
            if item["product"]["id"] == p["id"]:
                item["quantity"] += quantity
                p['stock'] -= quantity
                update_stock_in_db(p['id'], -quantity)
                update_cart()
                load_products(search_box.value, current_category)
                return
        cart.append({"product": p, "quantity": quantity})
        p['stock'] -= quantity
        update_stock_in_db(p['id'], -quantity)
        update_cart()
        load_products(search_box.value, current_category)

    def load_products(filter_text="", category="All"):
        global current_category
        current_category = category
        db_products = load_products_from_db(filter_text, category)
        grid.controls.clear()
        for p in db_products:
            quantity_field = ft.TextField(
                value="1",
                width=60,
                height=35,
                text_size=12,
                text_align="center",
                keyboard_type=ft.KeyboardType.NUMBER,
                border_radius=10,
                color="BLACK",
                border_color="#00CED1"
            )
            card = ft.Container(
                bgcolor="white",
                border_radius=15,
                padding=10,
                shadow=ft.BoxShadow(blur_radius=10, color="#00CED1"),
                content=ft.Column([
                    ft.Image(src=p["img"], width=80, height=80, fit="contain"),
                    ft.Text(p["name"], weight="bold", size=14, color="#006D77"),
                    ft.Text(f"₱{p['price']}", color="#0096c7", size=12),
                    ft.Text(f"Stock: {p['stock']}", size=10, color="green" if p['stock'] >= 10 else "orange"),
                    ft.Row([
                        quantity_field,
                        ft.ElevatedButton(
                            "Add to cart",
                            bgcolor="#00B4D8",
                            color="white",
                            on_click=lambda e, prod=p, qf=quantity_field: add_to_cart(prod,
                                                                                      int(qf.value) if qf.value.isdigit() else 1)
                        )
                    ], alignment="center", spacing=5)
                ], alignment="center", horizontal_alignment="center"),
            )
            grid.controls.append(card)
        page.update()

    def search_changed(e):
        load_products(search_box.value, current_category)

    def filter_by_category(e, cat):
        load_products(search_box.value, cat)

    def create_main_view():
        sidebar = create_sidebar("home")
        products_container = ft.Container(
            expand=True,
            content=ft.Column([
                header,
                create_categories_row(),
                grid
            ], expand=True)
        )
        main_row = ft.Row([
            sidebar,
            products_container,
            cart_section
        ], expand=True)
        stack = ft.Stack([
            main_row,
            receipt_overlay
        ], expand=True)
        return ft.View("/main", [stack])

    def create_categories_row():
        global current_category
        category_buttons = [
            ft.OutlinedButton("All", on_click=lambda e: filter_by_category(e, "All"),
                              style=ft.ButtonStyle(color={"": "#0077b6" if current_category == "All" else "#0096c7"})),
            ft.OutlinedButton("Phone", on_click=lambda e: filter_by_category(e, "Phone"),
                              style=ft.ButtonStyle(
                                  color={"": "#0077b6" if current_category == "Phone" else "#0096c7"})),
            ft.OutlinedButton("Laptop", on_click=lambda e: filter_by_category(e, "Laptop"),
                              style=ft.ButtonStyle(
                                  color={"": "#0077b6" if current_category == "Laptop" else "#0096c7"})),
            ft.OutlinedButton("Tablet", on_click=lambda e: filter_by_category(e, "Tablet"),
                              style=ft.ButtonStyle(
                                  color={"": "#0077b6" if current_category == "Tablet" else "#0096c7"})),
            ft.OutlinedButton("Camera", on_click=lambda e: filter_by_category(e, "Camera"),
                              style=ft.ButtonStyle(
                                  color={"": "#0077b6" if current_category == "Camera" else "#0096c7"})),
            ft.OutlinedButton("Mouse", on_click=lambda e: filter_by_category(e, "Mouse"),
                              style=ft.ButtonStyle(
                                  color={"": "#0077b6" if current_category == "Mouse" else "#0096c7"})),
            ft.OutlinedButton("Monitor", on_click=lambda e: filter_by_category(e, "Monitor"),
                              style=ft.ButtonStyle(
                                  color={"": "#0077b6" if current_category == "Monitor" else "#0096c7"})),
            ft.OutlinedButton("Accessories", on_click=lambda e: filter_by_category(e, "Accessories"),
                              style=ft.ButtonStyle(
                                  color={"": "#0077b6" if current_category == "Accessories" else "#0096c7"})),
            ft.OutlinedButton("Drone", on_click=lambda e: filter_by_category(e, "Drone"),
                              style=ft.ButtonStyle(
                                  color={"": "#0077b6" if current_category == "Drone" else "#0096c7"})),
        ]
        return ft.Row(category_buttons, scroll="auto")

    def create_stock_view():
        db_products = load_products_from_db()
        stock_content = ft.Container(
            expand=True,
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#E6F7FA", "#00B4D8"]
            ),
            content=ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color="#023e8a",
                        on_click=lambda e: page.go("/main")
                    ),
                    ft.Row(
                        controls=[
                            ft.Image(
                                src="https://scontent.ftdg1-1.fna.fbcdn.net/v/t1.15752-9/553712766_773496482176943_5255931375596611872_n.png?_nc_cat=110&ccb=1-7&_nc_sid=9f807c&_nc_eui2=AeGvY804cTN1HgIlJgKaDv1KLPWtOmpj0Jgs9a06amPQmDOKYB52U0srOOynT1bjxsL95nYEDYk9VXl_AUaj9uG9&_nc_ohc=QauxEQDhpesQ7kNvwFB9uUW&_nc_oc=AdnHjhUcOuKhhzlWfkfTWZ_nJ1VOgp5ar5u1nCAunmWa-bw7GqqbWKu8ciaGakpHlJo&_nc_zt=23&_nc_ht=scontent.ftdg1-1.fna&oh=03_Q7cD3gGTBdXoBqX90bKQMsJCa4KM2A9PgRge-PEW9TWdELnsZA&oe=6909B6C5&dl=1",
                                width=100,
                                height=100,
                                fit="contain"
                            ),
                            ft.Text("Stock Management", size=28, weight="bold", color="#023e8a"),
                            ft.Container(expand=True),
                        ]
                    )
                ]),
                ft.Divider(height=20),
                ft.Container(
                    expand=True,
                    bgcolor="white",
                    border_radius=15,
                    padding=20,
                    shadow=ft.BoxShadow(blur_radius=10, color="#00B4D8"),
                    content=ft.Column([
                        ft.Text("Product Inventory", size=20, weight="bold", color="#023e8a"),
                        ft.Divider(),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row([
                                        ft.Text("Product", expand=2, weight="bold", color="BLACK"),
                                        ft.Text("Category", expand=1, weight="bold", color="BLACK"),
                                        ft.Text("Price", expand=1, weight="bold", color="BLACK"),
                                        ft.Text("Stock  (Enter to Update)", expand=2, weight="bold", color="BLACK"),
                                    ], alignment="center"),
                                    ft.Divider(),
                                    *[
                                        ft.Row([
                                            ft.Row([
                                                ft.Image(src=p["img"], width=40, height=40),
                                                ft.Text(p["name"], expand=True, color="BLACK"),
                                            ], expand=2, alignment="start"),
                                            ft.Text(p["category"], expand=1, color="BLACK"),
                                            ft.Text(f"₱{p['price']}", expand=1, color="BLACK"),
                                            ft.Row([
                                                ft.Text(f"{p['stock']}", width=50, text_align="center", color="BLACK"),
                                                ft.TextField(
                                                    hint_text="Remove",
                                                    width=80,
                                                    height=30,
                                                    text_size=12,
                                                    text_align="center",
                                                    keyboard_type=ft.KeyboardType.NUMBER,
                                                    on_submit=lambda e, prod=p: adjust_stock(e, prod, False),
                                                    color="BLACK"
                                                ),
                                                ft.TextField(
                                                    hint_text="Add",
                                                    width=80,
                                                    height=30,
                                                    text_size=12,
                                                    text_align="center",
                                                    keyboard_type=ft.KeyboardType.NUMBER,
                                                    on_submit=lambda e, prod=p: adjust_stock(e, prod, True),
                                                    color="BLACK"
                                                ),
                                            ], expand=2),
                                        ], alignment="center")
                                        for p in db_products
                                    ]
                                ],
                                scroll="adaptive",
                            ),
                            expand=True
                        )
                    ])
                )
            ], scroll="adaptive")
        )
        sidebar = create_sidebar("stock")
        row = ft.Row([sidebar, stock_content], expand=True)
        return ft.View("/stock", [row])

    def create_stats_view():
        transactions = load_transactions_from_db()
        total_earnings = sum(t['total'] for t in transactions)
        total_transactions = len(transactions)
        today = datetime.now().date()
        today_sales = sum(t['total'] for t in transactions if t['timestamp'].date() == today)
        db_products = load_products_from_db()
        total_stock_value = sum(p['price'] * p['stock'] for p in db_products)
        low_stock_items = [p for p in db_products if p['stock'] < 10]

        stats_content = ft.Container(
            expand=True,
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#E6F7FA", "#00B4D8"]
            ),
            content=ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color="#023e8a",
                        on_click=lambda e: page.go("/main")
                    ),
                    ft.Row(
                        controls=[
                            ft.Image(
                                src="https://scontent.ftdg1-1.fna.fbcdn.net/v/t1.15752-9/553712766_773496482176943_5255931375596611872_n.png?_nc_cat=110&ccb=1-7&_nc_sid=9f807c&_nc_eui2=AeGvY804cTN1HgIlJgKaDv1KLPWtOmpj0Jgs9a06amPQmDOKYB52U0srOOynT1bjxsL95nYEDYk9VXl_AUaj9uG9&_nc_ohc=QauxEQDhpesQ7kNvwFB9uUW&_nc_oc=AdnHjhUcOuKhhzlWfkfTWZ_nJ1VOgp5ar5u1nCAunmWa-bw7GqqbWKu8ciaGakpHlJo&_nc_zt=23&_nc_ht=scontent.ftdg1-1.fna&oh=03_Q7cD3gGTBdXoBqX90bKQMsJCa4KM2A9PgRge-PEW9TWdELnsZA&oe=6909B6C5&dl=1",
                                width=100,
                                height=100,
                                fit="contain",
                            ),
                            ft.Text("Business Statistics", size=28, weight="bold", color="#023e8a"),
                        ]
                    )
                ]),
                ft.Divider(height=20),
                ft.Row([
                    ft.Container(
                        expand=True,
                        height=120,
                        padding=20,
                        bgcolor="white",
                        border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=10, color="#00B4D8"),
                        content=ft.Column([
                            ft.Text("Total Earnings", size=16, color="#0077b6"),
                            ft.Text(f"₱{total_earnings:,.2f}", size=24, weight="bold", color="#023e8a"),
                        ])
                    ),
                    ft.Container(
                        expand=True,
                        height=120,
                        padding=20,
                        bgcolor="white",
                        border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=10, color="#00B4D8"),
                        content=ft.Column([
                            ft.Text("Today's Sales", size=16, color="#0077b6"),
                            ft.Text(f"₱{today_sales:,.2f}", size=24, weight="bold", color="#023e8a"),
                        ])
                    ),
                    ft.Container(
                        expand=True,
                        height=120,
                        padding=20,
                        bgcolor="white",
                        border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=10, color="#00B4D8"),
                        content=ft.Column([
                            ft.Text("Total Transactions", size=16, color="#0077b6"),
                            ft.Text(f"{total_transactions}", size=24, weight="bold", color="#023e8a"),
                        ])
                    ),
                ]),
                ft.Divider(height=30),
                ft.Container(
                    padding=20,
                    bgcolor="white",
                    border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=10, color="#00B4D8"),
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Stock Inventory", size=20, weight="bold", color="#023e8a"),
                            ft.Text(f"Total Stock Value: ₱{total_stock_value:,.2f}", color="#0077b6")
                        ]),
                        ft.Divider(),
                        ft.Column(
                            controls=[
                                ft.Row([
                                    ft.Image(src=p["img"], width=40, height=40),
                                    ft.Text(p["name"], expand=True, weight="bold", color="BLACK"),
                                    ft.Text(f"Stock: {p['stock']}",
                                            color="green" if p['stock'] >= 10 else "orange"),
                                    ft.Text(f"₱{p['price']} each", color="#0077b7"),
                                ]) for p in db_products
                            ],
                            scroll="adaptive",
                            height=200
                        ),
                        ft.Divider(),
                        ft.Text(f"⚠️ {len(low_stock_items)} items with low stock (<10 units)",
                                color="orange", weight="bold" if low_stock_items else None)
                    ])
                ),
                ft.Divider(height=20),
                ft.Container(
                    padding=20,
                    bgcolor="white",
                    border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=10, color="#00B4D8"),
                    content=ft.Column([
                        ft.Text("💳 Recent Transactions", size=20, weight="bold", color="#023e8a"),
                        ft.Divider(),
                        ft.Column(
                            controls=[
                                ft.Row([
                                    ft.Text(f"Transaction #{t['id']} ({t['payment_method']})", expand=True,
                                            color="BLACK"),
                                    ft.Text(f"SukiCard: {t['sukiCard'] if t['sukiCard'] else 'None'}", color="BLACK"),
                                    ft.Text(f"₱{t['total']:.2f}", weight="bold", color="BLACK"),
                                    ft.Text(t['timestamp'].strftime("%m/%d %H:%M"), color="grey"),
                                ]) for t in transactions
                            ] if transactions else [
                                ft.Text("No transactions yet", color="grey", italic=True)
                            ],
                            scroll="adaptive",
                            height=150
                        )
                    ])
                )
            ], scroll="adaptive")
        )
        sidebar = create_sidebar("statistics")
        row = ft.Row([sidebar, stats_content], expand=True)
        return ft.View("/statistics", [row])

    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(login_view)
        elif page.route == "/main":
            load_products()
            search_box.on_change = search_changed
            discount_checkbox.on_change = discount_changed
            page.views.append(create_main_view())
        elif page.route == "/stock":
            page.views.append(create_stock_view())
        elif page.route == "/statistics":
            page.views.append(create_stats_view())
        page.update()

    username_field = ft.TextField(
        label="Username",
        width=400,
        prefix_icon=ft.Icons.PERSON,
        color="WHITE",
        border_radius=20,
    )

    password_field = ft.TextField(
        label="Password",
        width=400,
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        color="WHITE",
        border_radius=20
    )

    login_button = ft.ElevatedButton(
        "Login",
        width=300,
        bgcolor="#00B4D8",
        color="white",
        on_click=login_clicked,
    )

    login_view = ft.View(
        "/",
        [
            ft.Container(
                expand=True,
                image=ft.DecorationImage(
                    src="https://chatgpt.com/backend-api/estuary/content?id=file_00000000e7dc61f88f04b8c5a52d513c&ts=489154&p=fs&cid=1&sig=38a4129b8fd69a134e211d8c2fa5da72cd1b384dc8f450bebbb56544c18bce0d&v=0",
                    fit=ft.ImageFit.COVER,
                ),
                alignment=ft.alignment.center,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["#023e8a", "#0096c7", "#0077b6"]
                ),
                content=ft.Container(
                    width=800,
                    height=550,
                    border_radius=25,
                    shadow=ft.BoxShadow(
                        blur_radius=200,
                        spread_radius=2,
                        color=ft.Colors.WHITE54,
                        offset=ft.Offset(0, 10)
                    ),
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Row(
                        [
                            ft.Container(
                                border_radius=10,
                                width=300,
                                height=470,
                                bgcolor=ft.Colors.BLACK54,
                                padding=40,
                                content=ft.Column(
                                    [
                                        ft.Container(
                                            alignment=ft.alignment.center,
                                            margin=ft.margin.only(bottom=5),
                                            content=ft.Column(
                                                [
                                                    ft.Image(
                                                        src="https://scontent.ftdg1-1.fna.fbcdn.net/v/t1.15752-9/557422905_1543372830163868_8222908200224575867_n.png?_nc_cat=101&ccb=1-7&_nc_sid=9f807c&_nc_eui2=AeGWb91tM_aT3G0ZjpMBfNcPgJyGdF3KuO6AnIZ0Xcq47hEEATh6Iz7uj3kodUkG4o5HgjzIhsFRtwvI9OOq6vsT&_nc_ohc=pAxyhkoDeAsQ7kNvwFqfulF&_nc_oc=Adm-6nSxxZ_LpnXv4Er83nRR-JXs2PbgItzypQVmgAB2rVVA3kUY36IoYTWyY9si-Z4&_nc_zt=23&_nc_ht=scontent.ftdg1-1.fna&oh=03_Q7cD3gFT59hNmoyxLBT9LUqoFrsK0_sAdF3HxVnXW4f-HU12Hw&oe=6907EA05&dl=1",
                                                        width=90,
                                                        height=90,
                                                        fit=ft.ImageFit.CONTAIN,
                                                    ),
                                                    ft.Text(
                                                        "AGOS",
                                                        size=40,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=ft.Colors.BLUE_600,
                                                    ),
                                                    ft.Text(
                                                        "Point of Sale System",
                                                        size=15,
                                                        color="#0096c7",
                                                        weight="bold"
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                spacing=0,
                                            )
                                        ),

                                        ft.Divider(
                                            thickness=50,
                                            color="TRANSPARENT"
                                        ),

                                        ft.Column(
                                            [
                                                ft.Column(
                                                    controls=[
                                                        username_field,
                                                        password_field,
                                                        ft.Container(height=10),
                                                    ],
                                                    alignment="CENTER"
                                                ),
                                                ft.Container(
                                                    content=login_button,
                                                    width=200,
                                                    alignment=ft.alignment.center
                                                ),

                                                ft.Container(
                                                    content=login_error_message,
                                                    width=200,
                                                    alignment=ft.alignment.center,
                                                    padding=ft.padding.only(top=10)
                                                ),

                                                ft.Container(height=10),

                                                ft.Text(
                                                    "© 2025 AGOS POS System",
                                                    size=10,
                                                    color=ft.Colors.WHITE38,
                                                    text_align=ft.TextAlign.CENTER
                                                )
                                            ],
                                            spacing=0,
                                        )
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                )
                            ),

                            ft.Container(
                                border_radius=10,
                                width=230,
                                height=470,
                                content=ft.Stack(
                                    [
                                        ft.Image(
                                            src="https://imgcdn.stablediffusionweb.com/2024/3/23/c367151a-f237-4ce1-be42-7553b3d37a9f.jpg",
                                            fit=ft.ImageFit.COVER,
                                            width=350,
                                            height=550
                                        ),
                                        ft.Container(
                                            gradient=ft.LinearGradient(
                                                begin=ft.alignment.center_left,
                                                end=ft.alignment.center_right,
                                                colors=[
                                                    ft.Colors.with_opacity(0.7, color=ft.Colors.BLACK54),
                                                    ft.Colors.with_opacity(0.3, "WHITE")
                                                ]
                                            ),
                                            width=350,
                                            height=550
                                        ),
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text(
                                                        "Welcome.",
                                                        size=25,
                                                        color=ft.Colors.WHITE,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    ft.Text(
                                                        "Streamlining Every Transaction with Ease.",
                                                        size=14,
                                                        color=ft.Colors.WHITE,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                alignment=ft.MainAxisAlignment.CENTER,
                                            ),
                                            padding=30,
                                            alignment=ft.alignment.center
                                        )
                                    ]
                                )
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=-16
                    )
                )
            )
        ],
        padding=0
    )

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main)
