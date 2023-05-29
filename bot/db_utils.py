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
