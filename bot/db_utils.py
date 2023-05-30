import sqlite3


def db_check_user(chat_id: int) -> tuple:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM adminpanel_users WHERE user_telegram = ?
    ''', (chat_id,))
    user = cursor.fetchone()
    database.close()
    return user


def db_register_user(chat_id: int, full_name: str) -> None:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO adminpanel_users(user_telegram, user_name) VALUES (?,?)
    ''', (chat_id, full_name))
    database.commit()
    database.close()


def db_update_user(chat_id: int, phone: str) -> None:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    UPDATE adminpanel_users SET user_phone = ? WHERE user_telegram = ?
    ''', (phone, chat_id))
    database.commit()
    database.close()


def db_create_user_cart(chat_id: int) -> None:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO adminpanel_carts(user_id_id) VALUES
    (
        (SELECT id FROM adminpanel_users WHERE user_telegram = ?)
    )
    ''', (chat_id,))

    database.commit()
    database.close()


def db_get_categories() -> list:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM adminpanel_categories;
    ''')
    categories = cursor.fetchall()
    database.close()
    return categories


def db_get_products(category_id: int) -> list:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    SELECT id, product_name FROM adminpanel_products WHERE product_category_id = ?
    ''', (category_id,))
    products = cursor.fetchall()
    database.close()
    return products


def db_get_product(product_id: int) -> tuple:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM adminpanel_products WHERE id = ?
    ''', (product_id,))
    product = cursor.fetchone()
    database.close()
    return product


def db_get_user_cart(chat_id: int) -> int:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    SELECT adminpanel_carts.id FROM adminpanel_carts 
    JOIN adminpanel_users 
    ON adminpanel_carts.user_id_id == adminpanel_users.id
    WHERE user_telegram == ?;
    ''', (chat_id,))
    cart_id = cursor.fetchone()[0]
    database.close()
    return cart_id


def db_update_to_cart(price: int, quantity: int, cart_id: int) -> None:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    UPDATE adminpanel_carts SET total_price=?, total_products=? WHERE id = ?
    ''', (price, quantity, cart_id))
    database.commit()
    database.close()
