#!/usr/bin/env python3

from utils.misc import *
from utils.request import *
from model import Content, JsonEncoder
from extract import *
from filters import *

import json, itertools
from urllib.parse import urljoin

def get_all_posts():
    import os.path
    from pkgutil import iter_modules
    from importlib import import_module

    package_dir = os.path.abspath(os.path.join(__file__, "../feeds"))
    def get_feeds_by_module():
        for (_, module_name, _) in iter_modules([package_dir]):
            with warn(Exception, func=module_name, msg=__name__):
                module = import_module(f"feeds.{module_name}")
                for url in module.get_feed():
                    print(module, url)
                    yield module, url
    modules, feed_urls = zip(*get_feeds_by_module())
    contents = async_aiohttp_get_all(feed_urls, ssl=False)
    for module, content in zip(modules, contents):
        if content:
            yield from module.parse_feed(content)
    

# def get_posts():
#     import multiprocessing

#     pool = multiprocessing.Pool(4)
#     return flatten(json.loads(obj) for obj in pool.map(task, modules()))


def parse_content(args):
    post, raw = args
    if not filter_raw(post, raw):
        return None
    with warn(Exception, msg=__name__):
        article = extract_article(post, raw)
        if not article:
            print('No article: ', post, file=sys.stderr)
            article = ''
        length = len(article)
        density = length/len(raw)
        limit = 1000
        raw = str(raw)
        filter_score=filter_pattern.subn('', article[:limit], 20)[1] + adblock_score(raw)
        return Content(post=post, raw=raw, article=article, density=density, length=length, filter_score=filter_score)

def normalize_url(post):
    if not post.link.startswith("http"):
        if post.link.startswith('/'):
            post.link = urljoin(post.source, post.link)
        else:
            post.link = 'https://' + post.link
    return post

def fetch_content(posts):
    posts = map(normalize_url, posts)
    pred = lambda post: post.link and post.link.startswith(post.source)
    async_posts, sync_posts = partition(pred, posts)
    texts = async_aiohttp_get_all(post.link for post in async_posts)
    yield from map(parse_content, zip(async_posts, texts))
    texts = sync_requests_get_all(post.link for post in sync_posts)
    yield from map(parse_content, zip(sync_posts, texts))

def summary(content):
    return Content(
        post=content.post,
        article=content.article[:40]+"...",
        length=len(content.article),
        density=content.density,
        filter_score=content.filter_score
    )

# TODO: filter by comments - OR relation

def deduplicate(posts):
    d = {}
    for post in reversed(posts):
        d[post.link] = post
    return list(d.values())

@timed
def main():
    from pprint import pprint
    import sys, operator
    from datetime import datetime, timezone
    import filters

    max_posts = 100
    now = datetime.now(None)

    all_posts = list(get_all_posts())
    posts = deduplicate(list(filter(None, all_posts)))
    # for content in fetch_content(posts):
    #     print(summary(content))
    # exit()
    filtered_posts = list(filter(filter_metadata, posts))
    rss, other = partition(lambda p: p.score < 0, filtered_posts)
    other.sort(key=lambda post: post.score + post.comment_count, reverse=True)
    # rss.sort(key=lambda post: post.date, reverse=True)
    # interleave
    filtered_posts = [x for x in itertools.chain(*itertools.zip_longest(rss, other)) if x is not None]
    contents = list(fetch_content(filtered_posts[:max_posts]))
    filtered_contents = list(filter(filter_content, contents))
    coeff = 1/(filters.max_filter_score + filters.max_adblock_score)
    pred = lambda content: 100 * approx_distance(2*content.density, (1-coeff*content.filter_score)) + content.post.score + content.post.comment_count
    filtered_contents.sort(key=pred, reverse=True)
    top_contents = filtered_contents[:max_posts]
    print(json.dumps(list(map(summary, top_contents)), indent=4, cls=JsonEncoder, ensure_ascii=False))
    print(f'{len(top_contents)}/{len(filtered_contents)}/{len(contents)}/{len(filtered_posts)}/{len(posts)}/{len(all_posts)}', file=sys.stderr)

if __name__=="__main__":
    main()