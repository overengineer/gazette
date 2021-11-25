from model import Post, Content

try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)

def read_filter_file(filter_path):
    with open(filter_path) as fd:
        for line in fd:
            line = line.strip()
            # skip blank lines
            if len(line) < 3:
                continue
            # skip comments
            if re.match(r'^#', line):
                continue
            yield line

def get_filter_pattern(filter_path="data/filter.txt"):
    patterns = read_filter_file(filter_path)
    combined = "(" + ")|(".join(patterns) + ")"
    return re.compile(combined)

filter_pattern = get_filter_pattern()

def filter_metadata(post):
    n = 2
    return post and post.link and post.title and post.comment_count >= n and not filter_pattern.match(post.link + '\n' + post.title)

def filter_content(content):
    n = 10
    limit = 1000
    return content.article and content.density > 0.05 and filter_pattern.subn('', content.article[:limit], n)[1] < n
