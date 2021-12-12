
import sys
from glob import glob
import feedparser
from model import *

def parse_feed(content):
    if not content:
        return
    feed = feedparser.parse(content)
    for entry in feed.entries:
        yield Post(**entry)

def get_feed():
    with open('assets/rss/feeds.txt') as fd:
        for url in fd:
            if len(url) < 10:
                continue
            url = url.strip()
            if url[0] != '#':
                yield url.strip()