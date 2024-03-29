import sys, time, contextlib

# https://stackoverflow.com/a/8290508
def batches(iterable, n=1):
    l = len(iterable)
    for ndx in range(0,l,n):
        yield iterable[ndx:min(ndx + n, l)]

def datetime_from_iso(s):
    from datetime import datetime
    return datetime.strptime(s, r"%Y-%m-%dT%H:%M:%S")

def empty_generator():
    return
    yield

def flatten(nested):
    for iterable in nested:
        yield from iterable

# https://stackoverflow.com/a/46217079
def partition(p, l):
    x = [], []
    for n in l: x[p(n)].append(n)
    return x

@contextlib.contextmanager
def warn(*exceptions, func='', msg=''):
    try:
        yield
    except exceptions as ex:
        print(msg, func, type(ex), ex, file=sys.stderr)

# https://www.flipcode.com/archives/Fast_Approximate_Distance_Functions.shtml
def approx_distance(*args):
    return 0.43*min(*args) + max(*args)

# 
def timed(func):
    """
    records approximate durations of function calls
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = "{name:<30} finished in {elapsed:.2f} seconds".format(
            name=func.__name__, elapsed=time.time() - start
        )
        print(duration, file=sys.stderr)
        timed.durations.append(duration)
        return result
    return wrapper

timed.durations = []


from datetime import datetime, timezone
LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo
