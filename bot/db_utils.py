import sqlite3


def db_check_user(chat_id: int) -> tuple | None:
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
    INSERT INTO adminpanel_carts(user_id) VALUES
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


def db_get_user_cart(chat_id: int) -> tuple:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute(f'''
    SELECT adminpanel_carts.id, adminpanel_carts.total_price, adminpanel_carts.total_products
    FROM adminpanel_carts JOIN adminpanel_users 
    ON adminpanel_carts.user_id == adminpanel_users.id
    WHERE user_telegram == ?;
    ''', (chat_id,))
    cart_id = cursor.fetchone()
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


def db_get_product_by_name(product_name: str) -> tuple:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_price, product_info, product_image
    FROM adminpanel_products WHERE product_name = ?
    ''', (product_name,))
    product_info = cursor.fetchone()
    database.close()
    return product_info


def db_ins_or_upd_finally_cart(
        cart_id: int, product_name: str, total_products: int, total_price: int
) -> bool:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    try:
        cursor.execute('''
        INSERT INTO adminpanel_finally_carts (cart_id, product_name, product_quantity, final_price )
        VALUES (?, ?, ?, ?)
        ''', (cart_id, product_name, total_products, total_price))
        return True
    except sqlite3.IntegrityError:
        cursor.execute('''
        UPDATE adminpanel_finally_carts SET product_quantity = ?,  final_price = ?
        WHERE product_name = ? AND cart_id = ?
        ''', (total_products, total_price, product_name, cart_id))
        return False
    finally:
        database.commit()
        database.close()


def db_get_cart_products(chat_id: int, delete: bool = False) -> list:
    if delete:
        columns = '''
                  adminpanel_finally_carts.id, 
                  adminpanel_finally_carts.product_name
                  '''
    else:
        columns = '''
                  adminpanel_finally_carts.product_name, 
                  adminpanel_finally_carts.product_quantity, 
                  adminpanel_finally_carts.final_price,
                  adminpanel_finally_carts.cart_id
                  '''

    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute(f'''
    SELECT {columns}
    FROM adminpanel_finally_carts 
    JOIN adminpanel_carts 
          ON adminpanel_finally_carts.cart_id == adminpanel_carts.id
    JOIN adminpanel_users
          ON adminpanel_carts.user_id == adminpanel_users.id
    WHERE user_telegram == ?;
    ''', (chat_id,))
    products = cursor.fetchall()
    database.close()
    return products


def db_delete_product(finally_id: int) -> None:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    DELETE FROM adminpanel_finally_carts WHERE id = ?
    ''', (finally_id,))
    database.commit()
    database.close()


def db_get_final_price(chat_id: int) -> int | None:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
    SELECT sum(adminpanel_finally_carts.final_price) 
    FROM adminpanel_finally_carts 
    JOIN adminpanel_carts 
        ON adminpanel_carts.id = adminpanel_finally_carts.cart_id
    JOIN adminpanel_users 
        ON adminpanel_users.id = adminpanel_carts.user_id 
    WHERE adminpanel_users.user_telegram = ?
    ''', (chat_id,))
    summary_price = cursor.fetchone()
    database.close()
    return summary_price[0]


def clear_finally_cart(cart_id: int) -> None:
    database = sqlite3.connect('../management/db.sqlite3')
    cursor = database.cursor()
    cursor.execute('''
     DELETE FROM adminpanel_finally_carts WHERE cart_id = ?
    ''', (cart_id, ))
    database.commit()
    database.close()
