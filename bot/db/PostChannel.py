from collections import namedtuple

from .SQLite import Sqlite3_Database


class PostChannel:
    def __init__(self, id, **kwargs):
        self.id: int = id
        if len(kwargs):
            self.id_post = kwargs.get('id_post')
            self.id_channel = kwargs.get('id_channel')

        else:
            self.id_post = 0
            self.id_channel = 0

    def __iter__(self):
        dict_class = self.__dict__
        Result = namedtuple("Result", ["name", "value"])
        for attr in dict_class:
            if not attr.startswith("__"):
                if attr != "flag":
                    yield Result(attr, dict_class[attr])
                else:
                    yield Result(attr, dict_class[attr].value)


class PostChannels(Sqlite3_Database):
    def __init__(self, db_file_name, table_name, *args) -> None:
        Sqlite3_Database.__init__(self, db_file_name, table_name, *args)
        self.len = len(self.get_keys())

    def add(self, obj: PostChannel) -> None:
        self.add_row(obj)
        self.len += 1

    def __len__(self):
        return self.len

    def __delitem__(self, key):
        self.del_instance(key)
        self.len -= 1

    def __iter__(self) -> PostChannel:
        keys = self.get_keys()
        for id in keys:
            obj = self.get(id)
            yield obj

    def get_channels(self, id):
        data = self.get_by_other_field(value=id, field="id_post", att2="id_channel")
        resp = []
        for id in data:
            resp.append(id[0])
        return resp

    def get(self, id: int) -> PostChannel | bool:
        if id in self:
            obj_tuple = self.get_elem_sqllite3(id)
            obj = PostChannel(id=obj_tuple[0],
                              id_post=obj_tuple[1],
                              id_channel=obj_tuple[2],
                              )
            return obj
        return False



