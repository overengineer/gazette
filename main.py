#!/usr/bin/env python3

from utils.misc import *
from utils.request import *
from model import Content
from extract import *

import json

def get_all_posts():
    import os.path
    from pkgutil import iter_modules
    from importlib import import_module

    package_dir = os.path.abspath(os.path.join(__file__, "../sources"))
    for (_, module_name, _) in iter_modules([package_dir]):
        with warn(Exception, func='get_all_posts'):
            module = import_module(f"sources.{module_name}")
            yield from module.fetch_feed()

# def get_posts():
#     import multiprocessing

#     pool = multiprocessing.Pool(4)
#     return flatten(json.loads(obj) for obj in pool.map(task, modules()))


def parse_content(post, raw):
    if not raw:
        print("No text:", post, file=sys.stderr)
        return None
    with warn(Exception):
        article = extract_article(raw)
        if not article:
            print('No article: ', post, file=sys.stderr)
            article = ''
        density = len(article)/len(raw)
        return Content(post=post, article=article, density=density)


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
        density=content.density
    )

# TODO: filter by comments - OR relation

@timed
def main():
    from filters import filter_metadata,filter_content
    from pprint import pprint
    import sys
    
    all_posts = list(get_all_posts())
    posts = list(filter(None, all_posts))
    filtered_posts = list(filter(filter_metadata, posts))
    contents = list(fetch_content(filtered_posts))
    filtered_contents = list(filter(filter_content, contents))
    print(json.dumps(list(summary(content) for content in filtered_contents), indent=4))
    print(f'{len(filtered_contents)}/{len(contents)}/{len(filtered_posts)}/{len(posts)}/{len(all_posts)}', file=sys.stderr)

if __name__=="__main__":
    main()