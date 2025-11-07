import sqlite3

from bot.config import DB_PATH


def execute_query(query: str, params: tuple = ()) -> list:
    with sqlite3.connect(f"{DB_PATH}") as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        if query.strip().upper().startswith('SELECT'):
            return cursor.fetchall()
        connection.commit()


# добавить тег в бд
def Create_tag(tag: str) -> None:
    execute_query("INSERT INTO Tags (name_tag) VALUES (?)", (tag,))


# удалить тег из бд
def Delete_tag(tag: str) -> None:
    execute_query("DELETE FROM Tags WHERE name_tag = ?", (tag,))


# переименовать тег в бд
def Rename_tag(old_tag: str, new_tag: str) -> None:
    execute_query(f"UPDATE Tags SET name_tag = ? WHERE name_tag = ?", (new_tag, old_tag))


def Edit_description(new_description: str, tag_name: str):
    execute_query(f"UPDATE Tags SET description = ? WHERE name_tag = ?", (new_description, tag_name))


# получить список всех тегов в бд
def Get_tags() -> list:
    return execute_query("SELECT name_tag FROM Tags")


# получить id тега из бд
def Get_id_tag(name: str) -> list:
    return execute_query("SELECT id FROM Tags WHERE name_tag = ?", (name,))


# добавить пользователя в бд
def Add_user(identifier: int, name: str) -> None:
    execute_query("INSERT INTO Users (id, name_user) VALUES (?, ?)", (identifier, name))


# удалить пользователя из бд
def Delete_user(name: str) -> None:
    execute_query("DELETE FROM Users WHERE name_user = ?", (name,))


# получить всех пользователей в бд
def Get_users() -> list:
    return execute_query("SELECT name_user FROM Users")


# получить id пользователя из бд
def Get_id_user(name: str) -> list:
    return execute_query("SELECT id FROM Users WHERE name_user = ?", (name,))


# связать пользователя с тегом
def Link_user_tag(name: str, tag: str) -> None:
    id_user = execute_query("SELECT id FROM Users WHERE name_user = ?", (name,))  # возвращает кортеж
    id_tag = execute_query("SELECT id FROM Tags WHERE name_tag = ?", (tag,))  # возвращает кортеж
    id_user = id_user[0][0]  # Достаем ID пользователя из кортежа
    id_tag = id_tag[0][0]  # Достаем ID тега из кортежа
    execute_query("INSERT INTO Lnk_tag_name (tag_id, user_id) VALUES (?, ?)", (id_tag, id_user))


# удалить пользователя из тега
def Delete_user_from_tag(name: str, tag: str) -> None:
    id_user = execute_query("SELECT id FROM Users WHERE name_user = ?", (name,))  # возвращает кортеж
    id_tag = execute_query("SELECT id FROM Tags WHERE name_tag = ?", (tag,))  # возвращает кортеж
    id_user = id_user[0][0]  # Достаем ID пользователя из кортежа
    id_tag = id_tag[0][0]  # Достаем ID тега из кортежа
    execute_query("DELETE FROM Lnk_tag_name WHERE tag_id = ? AND user_id = ?", (id_tag, id_user))


# получить список пользователей в теге
def Get_users_from_tag(tag_name: str) -> list:
    return execute_query("SELECT name_user FROM Users "
                         "JOIN Lnk_tag_name ON Users.id = Lnk_tag_name.user_id "
                         "JOIN Tags ON Lnk_tag_name.tag_id = Tags.id "
                         "WHERE Tags.name_tag = ?", (tag_name,))


# добавить день рождения в бд
def Add_birth_date(birth_date: str, identifier: int) -> None:
    execute_query("UPDATE Users SET birth_date = ? WHERE id = ?", (birth_date, identifier))


# получить описание тега из бд
def Get_tag_description(name: str) -> list:
    return execute_query("SELECT description FROM Tags WHERE name_tag = ?", (name,))


def Get_users_with_birth_date() -> list:
    return execute_query("SELECT name_user, birth_date FROM Users")


def Get_users_for_send_message_about_birthday(name: str) -> list:
    return execute_query("SELECT id, name_user FROM Users WHERE name_user != ?", (name,))


def Get_user_by_id(id_user: int):
    return execute_query("SELECT name_user FROM Users WHERE id = ?", (id_user,))


def Check_tag_name(name: str) -> bool:
    if execute_query("SELECT EXISTS (SELECT name_tag FROM Tags WHERE name_tag = ?)", (name,)) == [(0,)]:
        return False
    else:
        return True


def Add_description_to_tag(tag_name: str, description: str):
    execute_query("UPDATE Tags SET description = ? WHERE name_tag = ?", (description, tag_name))


def Get_users_not_in_tag(tag_name: str):
    return execute_query("""
        SELECT name_user 
        FROM Users 
        WHERE id NOT IN (
            SELECT user_id 
            FROM Lnk_tag_name 
            JOIN Tags ON Lnk_tag_name.tag_id = Tags.id 
            WHERE Tags.name_tag = ?
        )
    """, (tag_name,))


def Get_users_not_in_the_list(list_users: list):
    if not list_users:
        return execute_query("SELECT name_user FROM Users")

        # Создаем нужное количество плейсхолдеров
    placeholders = ','.join(['?' for _ in list_users])
    query = f"SELECT name_user FROM Users WHERE name_user NOT IN ({placeholders})"
    return execute_query(query, tuple(list_users))


def Get_users_to_spam():
    return execute_query("SELECT id_user FROM Spam")


def Get_count_column():
    return execute_query("SELECT COUNT(*) FROM pragma_table_info('Spam')")[0][0]


def Delete_column_by_name_in_Spam(day: str):
    execute_query(f'ALTER TABLE Spam DROP COLUMN "{day}"')


def Add_column_by_name_in_Spam(day: str):
    execute_query(f'ALTER TABLE Spam ADD COLUMN "{day}" TEXT NOT NULL DEFAULT "Не заполнял"')


def Change_state_in_Spam(state: str, day: str, id_user: int):
    execute_query(f'UPDATE Spam SET "{day}" = "{state}" WHERE id_user = {id_user}')


def Check_admin(id_user: int) -> bool:
    return True if execute_query(f"SELECT * FROM Users WHERE id = {id_user} AND is_admin = 'Yes'") != [] else False


def Get_admins_id():
    return execute_query("SELECT id FROM Users WHERE is_admin = 'Yes'")


def Get_tracking_days():
    return execute_query('SELECT name FROM pragma_table_info("Spam")')


def Get_tracking_users(day: str):
    return execute_query(f'SELECT name_user, "{day}" FROM Spam')


def Get_users_ids():
    return execute_query("SELECT id FROM Users")


# смена состояния при отправке денег
def Sent_money(id_user: int):
    execute_query(f"UPDATE Sponsors SET 'is_payment' = 'Yes' WHERE id_user = {id_user}")


# каждый месяц сбрасывается список отправивших деньги
def Reset_sent_money():
    execute_query("UPDATE Sponsors SET 'is_payment' = 'No'")


# проверка на тех, кто ещё не скинул деньги
def Check_sent_money_group():
    return execute_query("SELECT id_user FROM Sponsors WHERE is_payment = 'No'")


# проверка конкретного пользователя на отправку денег
def Check_sent_money_person(id_user: int) -> bool:
    return True if execute_query(f"SELECT id_user FROM Sponsors "
                                 f"WHERE is_payment = 'No' AND id_user = {id_user}") == [] else False
