from collections import namedtuple

from .SQLite import Sqlite3_Database


class Channel:
    def __init__(self, id, **kwargs):
        self.id: int = id
        if len(kwargs):
            self.name: str = kwargs.get('name')
            self.count_user: int = kwargs.get('count_user')
            self.signing: str = kwargs.get('signing')
            self.link: str = kwargs.get('link')
            self.confirm_public: bool = bool(kwargs.get('confirm_public'))
            self.empty_string: bool = bool(kwargs.get('empty_string'))

        else:
            self.name: str = ""
            self.count_user: int = 0
            self.signing: str = ""
            self.link: str = ""
            self.confirm_public: bool = True
            self.empty_string: bool = False

    def __iter__(self):
        dict_class = self.__dict__
        Result = namedtuple("Result", ["name", "value"])
        for attr in dict_class:
            if not attr.startswith("__"):
                if attr != "flag":
                    yield Result(attr, dict_class[attr])
                else:
                    yield Result(attr, dict_class[attr].value)


class Channels(Sqlite3_Database):
    def __init__(self, db_file_name, table_name, *args) -> None:
        Sqlite3_Database.__init__(self, db_file_name, table_name, *args)
        self.len = len(self.get_keys())

    def add(self, obj: Channel) -> None:
        self.add_row(obj)
        self.len += 1

    def __len__(self):
        return self.len

    def __delitem__(self, key):
        self.del_instance(key)
        self.len -= 1

    def __iter__(self) -> Channel:
        keys = self.get_keys()
        for id in keys:
            obj = self.get(id)
            yield obj

    def get(self, id: int) -> Channel | bool:
        if id in self:
            obj_tuple = self.get_elem_sqllite3(id)
            obj = Channel(
                id=obj_tuple[0],
                name=obj_tuple[1],
                count_user=obj_tuple[2],
                signing=obj_tuple[3],
                link=obj_tuple[4],
                confirm_public=obj_tuple[5],
                empty_string=obj_tuple[6],
            )
            return obj
        return False
