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
    voters_, details_ = entry('div')[0]('div')
    link_, tags_, byline_ = details_

    titlelink = link_('a')
    if "nofollow" in titlelink.attrs.get("rel",[]):
        return None

    link = titlelink.get("href")
    if link.startswith("/"):
        link = urljoin(base_url, link)

    return Post(
        title=titlelink.string,
        link=link,
        score=int(voters('div').string),
        user=f'',
        date='',
        comments=f'',
        comment_count=0,
        source=base_url,
        tags=[a.string for a in tags_('a')]
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

    for content in sync_requests_get_all(uris):
        with warn(Exception, func='fetch_feed'):
            yield from parse_feed(content)
