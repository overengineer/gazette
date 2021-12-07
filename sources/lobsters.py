from model import Post
from utils.misc import *
from utils.request import *

from datetime import datetime
import requests
from bs4 import BeautifulSoup
import cchardet
from contextlib import suppress
from urllib.parse import urlsplit, urljoin

base_url = "https://lobste.rs/"

def parse_post(story):
    score = int(story('div', class_='score')[0].text)
    titlelink_, = story('a', class_='u-url')
    title = titlelink_.text
    link = titlelink_.get('href')
    tags = [a.text  for a in story('a', class_='tag')]
    author_, = story('a', class_='u-author')
    author = urljoin(base_url, author_.get('href'))
    date = author_.find_next('span').get('title')
    comments_, = story('span', class_='comments_label')[0]('a')
    comments = urljoin(base_url, comments_.get('href'))

    try:
        comment_count = int(comments_.text.strip().split()[0])
    except:
        comment_count = 0

    if "nofollow" in link:
        return None

    if link.startswith("/"):
        link = urljoin(base_url, link)

    return Post(
        title=title,
        link=link,
        score=score,
        user=author,
        date=datetime.strptime(date, r"%Y-%m-%d %H:%M:%S %z"),
        comments=comments,
        comment_count=comment_count,
        source=base_url,
        tags=tags
    )

def parse_feed(content):
    page = BeautifulSoup(content, 'lxml')
    stories = page('ol')[0].find_all('li')
    for story in stories:
        with warn(Exception, func='parse_feed'):
            yield parse_post(story)

def fetch_feed(n_pages=3):
    templ = "https://lobste.rs/page/{}"
    uris = (templ.format(page+1) for page in range(n_pages))

    for content in async_aiohttp_get_all(uris):
        with warn(Exception, func='fetch_feed'):
            yield from parse_feed(content)
