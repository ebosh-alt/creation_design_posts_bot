from collections import namedtuple

from .SQLite import Sqlite3_Database


class UrlButton:
    def __init__(self, id, **kwargs):
        self.id: int = id
        if len(kwargs):
            self.url = kwargs.get('url')
            self.id_button = kwargs.get('id_button')


        else:
            self.url = ""
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


class UrlButtons(Sqlite3_Database):
    def __init__(self, db_file_name, table_name, *args) -> None:
        Sqlite3_Database.__init__(self, db_file_name, table_name, *args)
        self.len = len(self.get_keys())

    def add(self, obj: UrlButton) -> None:
        self.add_row(obj)
        self.len += 1

    def __len__(self):
        return self.len

    def __delitem__(self, key):
        self.del_instance(key)
        self.len -= 1

    def __iter__(self) -> UrlButton:
        keys = self.get_keys()
        for id in keys:
            obj = self.get(id)
            yield obj

    def get(self, id: int) -> UrlButton | bool:
        if id in self:
            obj_tuple = self.get_elem_sqllite3(id)
            obj = UrlButton(id=obj_tuple[0],
                            url=obj_tuple[1],
                            id_button=obj_tuple[2],

                            )
            return obj
        return False
