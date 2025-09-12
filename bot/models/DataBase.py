import sqlite3


def execute_query(query: str, params: tuple = ()) -> list:
    with sqlite3.connect("C:\\Users\\user\\Desktop\\neotsort\\botik\\ArtEast_Studio_bot\\bot\\models\\"
                         "artEast_Studio_db.db") as connection:
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
    execute_query("INSERT INTO lnk_tag_name (tag_id, user_id) VALUES (?, ?)", (id_tag, id_user))


# удалить пользователя из тега
def Delete_user_from_tag(name: str, tag: str) -> None:
    id_user = execute_query("SELECT id FROM Users WHERE name_user = ?", (name,))  # возвращает кортеж
    id_tag = execute_query("SELECT id FROM Tags WHERE name_tag = ?", (tag,))  # возвращает кортеж
    id_user = id_user[0][0]  # Достаем ID пользователя из кортежа
    id_tag = id_tag[0][0]  # Достаем ID тега из кортежа
    execute_query("DELETE FROM lnk_tag_name WHERE tag_id = ? AND user_id = ?", (id_tag, id_user))


# получить список пользователей в теге
def Get_users_from_tag(tag_name: str) -> list:
    return execute_query("SELECT name_user FROM Users "
                         "JOIN lnk_tag_name ON Users.id = lnk_tag_name.user_id "
                         "JOIN Tags ON lnk_tag_name.tag_id = Tags.id "
                         "WHERE Tags.name_tag = ?", (tag_name,))


# добавить день рождения в бд
def Add_birth_date(birth_date: str, identifier: int) -> None:
    execute_query("UPDATE Users SET birth_date = ? WHERE id = ?", (birth_date, identifier))


# получить описание тега из бд
def Get_tag_information(name: str) -> list:
    return execute_query("SELECT description FROM Tags WHERE name_tag = ?", (name,))


def Get_users_with_birth_date() -> list:
    return execute_query("SELECT name_user, birth_date FROM Users")


def Get_users_for_send_message_about_birthday(name: str) -> list:
    return execute_query("SELECT id, name_user FROM Users WHERE name_user != ?", (name,))


def Check_tag_name(name: str) -> bool:
    if execute_query("SELECT EXISTS (SELECT name_tag FROM Tags WHERE name_tag = ?)", (name,)) == [(0,)]:
        return False
    else:
        return True


def Add_description_to_tag(tag_name: str, description: str):
    execute_query("UPDATE Tags SET description = ? WHERE name_tag = ?", (description, tag_name))
