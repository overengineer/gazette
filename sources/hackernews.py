from model import Post
from utils.misc import *
from utils.request import *

from datetime import datetime
import requests
from bs4 import BeautifulSoup
import cchardet
from contextlib import suppress
from urllib.parse import urlsplit, urljoin
from munch import Munch

base_url = "https://news.ycombinator.com"

def parse_post(entry, subtext):
    titlelink = entry('td')[2]('a')[0]

    if "nofollow" in titlelink.attrs.get("rel",[]):
        return None
    
    td = subtext('td')[1].find_all()

    if len(td) != 7:
        return None

    score, user, age, _, _, _, comments = td

    comment_count = 0
    s = comments.string.split()[0]
    if s.isdigit():
        comment_count = int(s)
    
    link = titlelink.get("href")
    if link.startswith("item?id="):
        link = urljoin("https://news.ycombinator.com", link)

    return Munch(
        title=titlelink.string,
        link=link,
        score=int(score.string.split()[0]),
        user=f'https://news.ycombinator.com/user?id={user.string}',
        date=age.get("title"),
        comments=f'https://news.ycombinator.com/{comments.get("href")}',
        comment_count=comment_count,
        source=base_url
    )

def parse_feed(content):
    page = BeautifulSoup(content, 'lxml')
    rows = page('table')[2].find_all('tr')[:-2]
    for entry, subtext, _ in batches(rows, 3):
        with warn(Exception):
            yield parse_post(entry, subtext)

def fetch_feed(n_pages=3):
    templ = "https://news.ycombinator.com/news?p={}"
    uris = (templ.format(page+1) for page in range(n_pages))

    for content in async_aiohttp_get_all(uris):
        with warn(Exception):
            yield from parse_feed(content)
