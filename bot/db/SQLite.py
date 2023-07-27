import sqlite3
from pathlib import Path


class Sqlite3_Database:
    def __init__(self, db_file_name: str, table_name: str, arguments=None, *args: dict) -> None:
        self.table_name = table_name
        self.db_file_name = db_file_name
        self.args = arguments

    def check(self):
        try:
            self.init_sqlite()
            return True
        except Exception as e:
            print(e.__repr__(), e.args)
            return False

    def creating_table(self) -> bool:
        if not self.is_file_exist():
            self.check()
        elif not self.is_table_exist():
            self.check()
        else:
            return True

    def sqlite_connect(self) -> sqlite3.Connection:  # Создание подключения к БД
        conn = sqlite3.connect(self.db_file_name, check_same_thread=False)
        conn.execute("pragma journal_mode=wal;")
        return conn

    def is_file_exist(self) -> bool:  # Существует ли файл БД
        db = Path(f"./{self.db_file_name}")
        try:
            db.resolve(strict=True)
            return True
        except FileNotFoundError:
            return False

    def is_table_exist(self) -> bool:
        conn = self.sqlite_connect()
        curs = conn.cursor()
        curs.execute(f'''SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name='{self.table_name}')''')
        is_exist = curs.fetchone()[0]
        conn.commit()
        conn.close()
        if is_exist:
            return True
        else:
            return False

    def init_sqlite(self) -> None:
        str_for_sql_req = ''
        if len(self.args) != 0:
            count = 1
            for key in self.args:
                if count == 1:
                    str_for_sql_req = str_for_sql_req + key + ' ' + self.args[key] + ' primary key'
                else:
                    str_for_sql_req = str_for_sql_req + key + ' ' + self.args[key]

                if count != len(self.args):
                    str_for_sql_req += ', '
                    count += 1
        conn = self.sqlite_connect()
        curs = conn.cursor()
        curs.execute(f'''CREATE TABLE {self.table_name} ({str_for_sql_req})''')
        # c.execute(f'''CREATE TABLE {table_name} (key integer primary key, user_id integer, user_name text,
        # user_surname text, username text)''')
        conn.commit()
        conn.close()

    def get_elem_sqllite3(self, id: int | str) -> tuple | bool:
        conn = self.sqlite_connect()
        curs = conn.cursor()
        if id.__class__.__name__ == "int":
            curs.execute(f'''SELECT * from {self.table_name} where id = {id}''')
        else:
            curs.execute(f'''SELECT * from {self.table_name} where id = '{id}' ''')
        answer = curs.fetchone()

        conn.close()

        return answer

    def __contains__(self, other: int | str) -> bool:
        conn = self.sqlite_connect()
        curs = conn.cursor()
        if other.__class__.__name__ == "int":
            curs.execute(f"SELECT 1 FROM {self.table_name} WHERE id={other}")
        else:
            curs.execute(f"SELECT 1 FROM {self.table_name} WHERE id='{other}'")
        if curs.fetchone() is not None:
            conn.close()
            return True
        else:
            conn.close()
            return False

    def add_row(self, obj) -> None:
        conn = self.sqlite_connect()
        curs = conn.cursor()
        insert_vals_str = ''
        values = list()
        for i in obj:
            values.append(i.value)
            insert_vals_str += "?,"
        insert_vals_str = insert_vals_str[:-1]
        curs.execute(f"""INSERT INTO {self.table_name} VALUES ({insert_vals_str})""", values)
        conn.commit()
        conn.close()

    def del_instance(self, id: int | str) -> None:
        conn = self.sqlite_connect()
        curs = conn.cursor()

        if id.__class__.__name__ == "int":
            curs.execute(f"""DELETE FROM {self.table_name} WHERE id = {id}""")
        else:
            curs.execute(f"""DELETE FROM {self.table_name} WHERE id = '{id}'""")
        conn.commit()
        conn.close()

    def update(self, obj) -> None:
        conn = self.sqlite_connect()
        curs = conn.cursor()
        for attr in obj:
            curs.execute(f"""UPDATE {self.table_name} SET {attr.name} = ? WHERE id = ?""", (attr.value, obj.id))

        conn.commit()
        conn.close()

    def get_keys(self) -> list:
        conn = self.sqlite_connect()
        curs = conn.cursor()
        curs.execute(f"""SELECT id FROM {self.table_name}""")
        grand_tuple = curs.fetchall()
        conn.commit()
        conn.close()
        keys = [key[0] for key in grand_tuple]
        return keys

    def get_attribute(self, attr: str):
        conn = self.sqlite_connect()
        curs = conn.cursor()
        curs.execute(f"""SELECT {attr} FROM {self.table_name}""")
        grand_tuple = curs.fetchall()
        conn.commit()
        conn.close()
        answer = [el[0] for el in grand_tuple]
        return answer

    def get_by_other_field(self, value: int | str, field: str, **kwargs) -> list:
        conn = self.sqlite_connect()
        curs = conn.cursor()
        if value.__class__.__name__ == "int":
            curs.execute(f'''SELECT {",".join(kwargs.values())} from {self.table_name} where {field} = {value}''')
        else:
            curs.execute(f'''SELECT {",".join(kwargs.values())} from {self.table_name} where {field} = '{value}' ''')

        answer = curs.fetchall()
        conn.close()
        return answer
