from collections import namedtuple

from .SQLite import Sqlite3_Database


class Button:
    def __init__(self, id, **kwargs):
        self.id: int = id
        if len(kwargs):
            self.name = kwargs.get('name')
            self.type = kwargs.get('type')
            self.number = kwargs.get('number')
            self.message_id = kwargs.get('message_id')

        else:
            self.name = ""
            self.type = "url"
            self.number = 0
            self.message_id = 0

    def __iter__(self):
        dict_class = self.__dict__
        Result = namedtuple("Result", ["name", "value"])
        for attr in dict_class:
            if not attr.startswith("__"):
                if attr != "flag":
                    yield Result(attr, dict_class[attr])
                else:
                    yield Result(attr, dict_class[attr].value)


class Buttons(Sqlite3_Database):
    def __init__(self, db_file_name, table_name, *args) -> None:
        Sqlite3_Database.__init__(self, db_file_name, table_name, *args)
        self.len = len(self.get_keys())

    def add(self, obj: Button) -> None:
        self.add_row(obj)
        self.len += 1

    def __len__(self):
        return self.len

    def __delitem__(self, key):
        self.del_instance(key)
        self.len -= 1

    def __iter__(self) -> Button:
        keys = self.get_keys()
        for id in keys:
            obj = self.get(id)
            yield obj

    def get(self, id: int) -> Button | bool:
        if id in self:
            obj_tuple = self.get_elem_sqllite3(id)
            obj = Button(id=obj_tuple[0],
                         name=obj_tuple[1],
                         type=obj_tuple[2],
                         number=obj_tuple[3],
                         message_id=obj_tuple[4],
                         )
            return obj
        return False
