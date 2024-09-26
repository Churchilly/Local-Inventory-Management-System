# storage.py
import sqlite3

DB_FILE_PATH = "market.db"


def initialize_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                barcode TEXT NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock REAL NOT NULL,
                PRIMARY KEY (barcode)
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_barcode ON items (barcode)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON items (name)")
    except:
        pass

    conn.close()


def load_data():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()
    return items


def add_product(barcode, name, price, stock):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO items (barcode, name, price, stock) VALUES (?, ?, ?, ?)
    """,
        (barcode, name, price, stock),
    )
    conn.commit()
    conn.close()


def item_exists(name):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT 1 FROM items WHERE name = ?
    """,
        (name,),
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def barcode_exists(barcode):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT 1 FROM items WHERE barcode = ?
    """,
        (barcode,),
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def reduce_stock(item_name, amount):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    UPDATE items SET stock = stock - ? WHERE name = ? AND stock >= ?
    """,
        (amount, item_name, amount),
    )
    conn.commit()
    conn.close()


def update_item_barcode(item_name, new_barcode):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    if new_barcode == "sil" or new_barcode == "del":
        cursor.execute(
            """
        DELETE FROM items WHERE name = ?
        """,
            (item_name,),
        )
    else:
        cursor.execute(
            """
        UPDATE items SET barcode = ? WHERE name = ?
        """,
            (new_barcode, item_name),
        )

    conn.commit()
    conn.close()


def update_item_name(item_name, new_name):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    UPDATE items SET name = ? WHERE name = ?
    """,
        (new_name, item_name),
    )
    conn.commit()
    conn.close()


def update_item_price(item_name, new_price):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    UPDATE items SET price = ? WHERE name = ?
    """,
        (new_price, item_name),
    )
    conn.commit()
    conn.close()


def update_item_stock(item_name, new_stock):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    UPDATE items SET stock = ? WHERE name = ?
    """,
        (new_stock, item_name),
    )
    conn.commit()
    conn.close()


def get_item_price(item_name):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT price FROM items WHERE name = ?
    """,
        (item_name,),
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
