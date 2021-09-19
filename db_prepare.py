""" Дни рождения
Karkyshka 14.12
burik 12.09
Шулаева Оксана 27.09
Вартас 22.03
Мотыль 31.10
Эксайтёр 08.12
Рома slalus 11.08
Света Луковская 30.05
megalohobot 19.03
Макс Шаар 22.01
Пабз 06.01
Alexandr Gorodnichev  12.08
Дашин Милый 25.06
Прокол 01.06
Лера Бурмистрова 18.01
Dgoo0 12.06
Женя Пятак 12.01
Рома розы 27.07
Рыба 21.08
Зебра 22.12
Гоблин 27.01
DARYAL 23.06
Князь Борис Бритва 01.11
83ND3R 07.07
"""

"""
/start - инициализация чата
"""
def start_command(user, chat):
    db_add_user(user)  # внутри проверка на существование юзера в БД
    db_add_chat(chat)  # внутри проверка на существование чата в БД
    print("Кого будем поздравлять в этом чате с ДР? Давай добавим юзеров.")
    print("Формат ввода:"
          "")



conn = sqlite3.connect("megalohobot.db")
cur = conn.cursor()

cur.execute(CREATE_TABLE_CHATS_QUERY)
cur.execute(CREATE_TABLE_USERS_QUERY)
cur.execute(CREATE_TABLE_USERS_IN_CHATS_QUERY)
conn.commit()


def main():
    db_init()
    start_bot()