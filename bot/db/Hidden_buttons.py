from collections import namedtuple

from .SQLite import Sqlite3_Database


class HiddenButton:
    def __init__(self, id, **kwargs):
        self.id: int = id
        if len(kwargs):
            self.text_by_subscriber = kwargs.get('text_by_subscriber')
            self.text_bu_not_subscriber = kwargs.get('text_bu_not_subscriber')
            self.id_button = kwargs.get('id_button')


        else:
            self.text_by_subscriber = ""
            self.text_bu_not_subscriber = ""
            self.id_button = 0

    def __iter__(self):
        dict_class = self.__dict__
        Result = namedtuple("Result", ["name", "value"])
        for attr in dict_class:
            if not attr.startswith("__"):
                if attr != "flag":
                    yield Result(attr, dict_class[attr])
                else:
                    yield Result(attr, dict_class[attr].value)


class HiddenButtons(Sqlite3_Database):
    def __init__(self, db_file_name, table_name, *args) -> None:
        Sqlite3_Database.__init__(self, db_file_name, table_name, *args)
        self.len = len(self.get_keys())

    def add(self, obj: HiddenButton) -> None:
        self.add_row(obj)
        self.len += 1

    def __len__(self):
        return self.len

    def __delitem__(self, key):
        self.del_instance(key)
        self.len -= 1

    def __iter__(self) -> HiddenButton:
        keys = self.get_keys()
        for id in keys:
            obj = self.get(id)
            yield obj

    def get(self, id: int) -> HiddenButton | bool:
        if id in self:
            obj_tuple = self.get_elem_sqllite3(id)
            obj = HiddenButton(id=obj_tuple[0],
                               text_by_subscriber=obj_tuple[1],
                               text_bu_not_subscriber=obj_tuple[2],
                               id_button=obj_tuple[3],

                               )
            return obj
        return False
