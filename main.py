#!/usr/bin/env python3

from utils.misc import *
from utils.request import *
from model import Content, JsonEncoder
from extract import *
from filters import *

import json, itertools

def get_all_posts():
    import os.path
    from pkgutil import iter_modules
    from importlib import import_module

    package_dir = os.path.abspath(os.path.join(__file__, "../feeds"))
    def get_feeds_by_module():
        for (_, module_name, _) in iter_modules([package_dir]):
            with warn(Exception, func=module_name):
                module = import_module(f"feeds.{module_name}")
                for url in module.get_feed():
                    yield module, url
    modules, feed_urls = zip(*get_feeds_by_module())
    contents = async_aiohttp_get_all(feed_urls)
    for module, content in zip(modules, contents):
        if content:
            yield from module.parse_feed(content)
    

# def get_posts():
#     import multiprocessing

#     pool = multiprocessing.Pool(4)
#     return flatten(json.loads(obj) for obj in pool.map(task, modules()))


def parse_content(post, raw):
    if not filter_raw(post, raw):
        return None
    with warn(Exception):
        article = extract_article(raw)
        if not article:
            print('No article: ', post, file=sys.stderr)
            article = ''
        length = len(article)
        density = length/len(raw)
        limit = 1000
        filter_score=filter_pattern.subn('', article[:limit], 20)[1]
        return Content(post=post, article=article, density=density, length=length, filter_score=filter_score)


def fetch_content(posts):
    pred = lambda post: post.link and post.link.startswith("https:/news.ycombinator.com")
    async_posts, sync_posts = partition(pred, posts)
    texts = async_aiohttp_get_all(post.link for post in async_posts)
    yield from (parse_content(post, text) for post, text in zip(async_posts, texts))
    texts = sync_requests_get_all(post.link for post in sync_posts)
    yield from (parse_content(post, text) for post, text in zip(sync_posts, texts))

def summary(content):
    return Content(
        post=content.post,
        article=content.article[:40]+"...",
        length=len(content.article),
        density=content.density,
        filter_score=content.filter_score
    )

# TODO: filter by comments - OR relation

@timed
def main():
    from pprint import pprint
    import sys, operator
    from datetime import datetime, timezone
    import filters

    max_posts = 100
    now = datetime.now(None)

    all_posts = list(get_all_posts())
    posts = list(filter(None, all_posts))
    filtered_posts = list(filter(filter_metadata, posts))
    filtered_posts.sort(key=lambda post: post.score, reverse=True)
    contents = list(fetch_content(filtered_posts[:50]))
    filtered_contents = list(filter(filter_content, contents))
    filtered_contents.sort(key=lambda content: content.density - (content.filter_score/filters.max_filter_score), reverse=True)
    top_contents = filtered_contents[:10]
    print(json.dumps(list(summary(content) for content in top_contents), indent=4, cls=JsonEncoder, ensure_ascii=False))
    print(f'{len(top_contents)}/{len(filtered_contents)}/{len(contents)}/{len(filtered_posts)}/{len(posts)}/{len(all_posts)}', file=sys.stderr)

if __name__=="__main__":
    main()