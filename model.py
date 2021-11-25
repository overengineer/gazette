from utils.misc import datetime_from_iso

from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, NamedTuple
import json

class Base:
    pass

class Post(NamedTuple):
    title: str
    link: str
    score: int
    user: str
    date: str
    comments: str
    comment_count: int
    source: str

class Content(NamedTuple):
    post: Post
    article: str
    density: int
    # summary: str
    # keywords: List[str]