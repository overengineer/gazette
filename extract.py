try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)

import sys

newl = re.compile("(\n[ \t\|]*)+")
space = re.compile("[ \t\|]+")

# https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/
def extract_article2(page):
    text = page.find_all(text=True)

    output = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head', 
        'input',
        'script',
        'style',
        'img',
        'a',
        'title'
    ]

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)

    output = newl.sub('\n', output)
    output = space.sub(' ', output)
    return output.strip()

def extract_article(raw):
    try:
        from trafilatura import extract
        config = {
            "date_extraction_params": {"extensive_search": True}, 
            "include_comments": False, 
            "include_tables": False, 
            "no_fallback": False,
            "favor_recall": True
        }
        article = extract(raw, **config)
        assert article
        return article
    except Exception as ex:
        print("extract_article", type(ex), ex, file=sys.stderr)
        from bs4 import BeautifulSoup
        page = BeautifulSoup(raw, 'lxml')
        return extract_article2(page)
