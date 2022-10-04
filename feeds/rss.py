
import sys
from glob import glob
import feedparser
from model import *

def parse_feed(content):
    if not content:
        return
    feed = feedparser.parse(content)
    for entry in feed.entries:
        kwargs = dict()
        kwargs['title'] = 'default'
        kwargs['link'] = 'default'
        kwargs['score'] = -1
        kwargs['user'] = 'default'
        kwargs['date'] = datetime.now()
        kwargs['comments'] = 'default'
        kwargs['comment_count'] = -1
        kwargs['source'] = 'default'
        kwargs |= entry
        # kwargs['content'] = ''
        # kwargs['summary'] = ''
        yield Post(**kwargs)

def get_feed():
    with open('assets/rss/feeds.txt') as fd:
        for url in fd:
            if len(url) < 10:
                continue
            url = url.strip()
            if url[0] != '#':
                yield url.strip()