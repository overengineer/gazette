from utils.misc import *
from contextlib import suppress

# https://stackoverflow.com/a/63179518
def async_aiohttp_get_all(urls, timeout=10, max_size=1000000, **kwargs):
    """
    performs asynchronous get requests
    """
    import asyncio
    from aiohttp import ClientSession, ClientTimeout
    from asgiref import sync

    async def get_all(urls):
        client_timeout = ClientTimeout(total=None, sock_connect=timeout, sock_read=timeout)
        async with ClientSession(timeout=client_timeout) as session:
            async def fetch(url):
                text = b''
                with warn(Exception), warn(asyncio.TimeoutError):
                    async with session.get(url, **kwargs) as response:
                        length = response.headers.get('Content-Length')
                        if length and int(length) > max_size:
                            raise ValueError('response too large')
                        size = 0
                        start = time.time()

                        async for chunk in response.content.iter_chunked(1024):
                            if time.time() - start > timeout:
                                raise ValueError('timeout reached')
                            size += len(chunk)
                            if size > max_size:
                                raise ValueError('response too large')

                            text += chunk
                return text
            return await asyncio.gather(*[
                fetch(url) for url in urls
            ])
    # call get_all as a sync function to be used in a sync context
    return sync.async_to_sync(get_all)(urls)

def sync_requests_get_all(urls, wait=1, timeout=10, **kwargs):
    import requests
    import cchardet
    import time
    session = requests.Session()
    for url in urls:
        text = b''
        with warn(Exception), suppress(requests.exceptions.ReadTimeout):
            # https://thehftguy.com/2020/07/28/making-beautifulsoup-parsing-10-times-faster/
            response = session.get(url, timeout=timeout, verify=True, stream=True, **kwargs)
            response.raw.decode_content = True
            text = response.raw
            time.sleep(wait)
        yield text

if __name__=="__main__":
    urls = [f'https://postman-echo.com/delay/{i}' for i in range(5)]

    timeout = 3

    @timed
    def test1():
        def gather(url):
            for results in async_aiohttp_get_all(urls, timeout=timeout):
                yield results
        print(list(gather(urls)))

    @timed
    def test2():
        def gather(url):
            for results in sync_requests_get_all(urls, timeout=timeout):
                yield results
        print(list(gather(urls)))

    test1()
    test2()

    
