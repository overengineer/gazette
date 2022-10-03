from munch import Munch
from typing import List
from datetime import datetime
import json

class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

class Base(Munch):
    def __init__(self, **kwargs):
        for key, typ in self.__annotations__.items():
            assert key in kwargs, f'missing field {key}'
            val = kwargs[key]
            assert isinstance(val, typ), f'field {key}:{val} is not instance of type {typ}'
        super().__init__(**kwargs)

class Post(Base):
    title: str
    link: str
    score: int
    user: str
    date: datetime
    comments: str
    comment_count: int
    source: str

class DefaultPost(Munch):
    title: str = 'default'
    link: str = 'default'
    score: int = 20
    user: str = 'default'
    date: datetime = datetime.now()
    comments: str = 'default'
    comment_count: int = 20
    source: str = 'default'

class Content(Base):
    post: Post
    article: str
    density: float
    length: int
    # summary: str
    # keywords: List[str]