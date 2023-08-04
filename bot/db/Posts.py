from collections import namedtuple

from .SQLite import Sqlite3_Database


class Post:
    def __init__(self, id, **kwargs):
        self.id: int = id
        if len(kwargs):
            self.text = kwargs.get('text')
            self.media = bool(kwargs.get('media'))
            self.button = bool(kwargs.get('button'))
            self.protect = bool(kwargs.get("protect"))
            self.time = int(kwargs.get('time'))
            self.duration = int(kwargs.get('duration'))
            self.delayed = kwargs.get('delayed')
            self.send_time = kwargs.get('send_time')
            self.end_posting = kwargs.get('end_posting')

        else:
            self.text = ""
            self.media = False
            self.button = False
            self.protect = False
            self.time = 0
            self.duration = 0
            self.delayed = ""
            self.send_time = 0
            self.end_posting = 0

    def __iter__(self):
        dict_class = self.__dict__
        Result = namedtuple("Result", ["name", "value"])
        for attr in dict_class:
            if not attr.startswith("__"):
                if attr != "flag":
                    yield Result(attr, dict_class[attr])
                else:
                    yield Result(attr, dict_class[attr].value)


class Posts(Sqlite3_Database):
    def __init__(self, db_file_name, table_name, *args) -> None:
        Sqlite3_Database.__init__(self, db_file_name, table_name, *args)
        self.len = len(self.get_keys())

    def add(self, obj: Post) -> None:
        self.add_row(obj)
        self.len += 1

    def __len__(self):
        return self.len

    def __delitem__(self, key):
        self.del_instance(key)
        self.len -= 1

    def __iter__(self) -> Post:
        keys = self.get_keys()
        for id in keys:
            obj = self.get(id)
            yield obj

    def get(self, id: int) -> Post | bool:
        if id in self:
            obj_tuple = self.get_elem_sqllite3(id)
            obj = Post(id=obj_tuple[0],
                       text=obj_tuple[1],
                       media=obj_tuple[2],
                       button=obj_tuple[3],
                       protect=obj_tuple[4],
                       time=obj_tuple[5],
                       duration=obj_tuple[6],
                       delayed=obj_tuple[7],
                       send_time=obj_tuple[8],
                       end_posting=obj_tuple[9],
                       )
            return obj
        return False
