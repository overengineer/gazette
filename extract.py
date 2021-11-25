try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)

newl = re.compile("(\n[ \t\|]*)+")
space = re.compile("[ \t\|]+")

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

def extract_article(page):
    try:
        from trafilatura import extract
        config = {
            "date_extraction_params": {"extensive_search": True}, 
            "include_comments": False, 
            "include_tables": False, 
            "no_fallback": False,
            "favor_recall": True
        }
        article = extract(page, **config)
        assert article
    except:
        return extract_article2(page)
