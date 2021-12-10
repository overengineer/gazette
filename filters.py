from model import Post

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
    return post and post.link and post.title and post.comment_count >= 2 and post.score >= 5 and not filter_pattern.match(post.link + '\n' + post.title)

def filter_raw(post, raw):
    return post and raw and 500000 >= len(raw) >= 1000

max_filter_score = 10

def filter_content(content):
    return content and 100000 >= content.length >= 100 and content.density > 0.05 and content.filter_score < max_filter_score

