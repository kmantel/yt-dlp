import json
import re

from .common import InfoExtractor


class StreamingCommunityIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?scws\.work/master/(?P<id>[0-9]+).*'

    _TESTS = [{
        'url': 'https://streamingcommunity.blue/watch/',
        'md5': 'TODO: md5 sum of the first 10241 bytes of the video file (use --test)',
        'info_dict': {
            'id': '',
            'ext': 'mp4',
            'title': '',
            'thumbnail': r're:^https?://.*\.jpg$',
            # TODO more properties, either as:
            # * A value
            # * MD5 checksum; start the string with md5:
            # * A regular expression; start the string with re:
            # * Any Python type, e.g. int or float
        }
    }]

    def __init__(self, *args, **kwargs):
        self._video_id = None
        super().__init__(*args, **kwargs)

    # _VIDEO_ID = None

    # def _get_video_id(url):
    #     if self._VIDEO_ID is not None:
    #         return self.VIDEO_ID
    #     else:
    #         return self._match_id(url)

    def _real_extract(self, url):
        video_id = self._video_id if self._video_id is not None else self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        work_url = f'https://scws.work/videos/{video_id}'
        data = json.loads(
            self._download_webpage(work_url, video_id)
        )

        # TODO more code goes here, for example ...
        # title = self._html_search_regex(r'<h1>(.+?)</h1>', webpage, 'title')

        match = re.match(r'.*type=(\w+)&rendition=(.*?)&.*', url)
        typ, rendition = match[1], match[2]
        cdn = data['cdn']
        fragments = []
        next_cdn_proxy_index = data['proxy_index']
        num_cdn_proxies = len(cdn['proxies'])

        for f in webpage.split('\n'):
            if len(f) == 0 or f[0] == '#':
                continue

            proxy_num = cdn['proxies'][next_cdn_proxy_index % num_cdn_proxies]['number']
            next_cdn_proxy_index += 1

            if '.m3u8' in rendition:
                resolution_str = ''
            else:
                resolution_str = f'/{typ}/{rendition}'

            frag_url = f'https://sc-{cdn["type"]}{cdn["number"]}-{proxy_num:02d}.{data["host"]}/hls/{data["storage"]["number"]}/{data["folder_id"]}{resolution_str}/{f}'

            fragments.append({
                'url': frag_url,
            })


        # formats = self._extract_m3u8_formats(url, video_id, ext='mp4', m3u8_id='hls')
        # [
        #     [x for x in webpage.split('\n') if x[0] != '#']
        # ]

        return {
            'id': video_id,
            'title': data['name'].replace(':', ''),
            # 'description': self._og_search_description(webpage),
            # 'uploader': self._search_regex(r'<div[^>]+id="uploader"[^>]*>([^<]+)<', webpage, 'uploader', fatal=False),
            # 'fragment_base_url': base_url,
            # 'formats': formats,
            'formats': [
                {
                    'fragments': fragments,
                    'url': url,
                    'manifest_url': url,
                    '_type': typ,
                    'protocol': 'm3u8_native',
                    'ext': 'mp4',
                },
            ],
            # TODO more properties (see yt_dlp/extractor/common.py)
        }


class StreamingCommunityListIE(StreamingCommunityIE):
    _VALID_URL = r'https?://(?:www\.)?streamingcommunity.(blue|bike)/watch/([0-9]+)\?e=(?P<id>[0-9]+)'
    _USER_AGENT = 'Mozilla/5.0 (X11; Linux i686; rv:47.0) Gecko/20100101 Firefox/47.0'
    _HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        # "Cookie": "cf_clearance=wAeukLs0I6YCuM7t3np18NG9zhOCcU99ipj0a7wUiR8-1676807849-0-250; XSRF-TOKEN=eyJpdiI6IkRUbGVHRzZlTkZYbVpRNVFQcW4rY1E9PSIsInZhbHVlIjoiYWxSY2dPK3p2aFNBYW8xRWg5SWltV3kzdUlINkNpVzBYcFExZGp4RFpZU0VNblU3am5NYUNyTnVQcGlLOWgySGJSYldNalRsWXFqRkRKK2RBdXBoMkJBMWo1dUt1bkhpajNnY1lrQ0VzeThDRk05dTdHeEdXWmxOeWJObk15cnUiLCJtYWMiOiI1NDA3ZDhiMzlhMjJiOGUzNThlOWI2OTlmYjNiM2Q4MTE1NjM1ODVhYjcyNjdlNjI3Mzg1N2QyMGYzZDM1ZDQ2In0%3D; streamingcommunity_session=eyJpdiI6IlBLMVpNTW40dCtZRW1MVkptbzczMUE9PSIsInZhbHVlIjoiaWxHUExUeFhRaW96NE9yMmMya21iVFNXVmZXMDJMS0dWUjlLdDJJQ3JzTHlsMXVcL2FtTFN6ZmhFUWdKWTR0QXhxVVVWbE0zbVB0d0dveFRDNW53cnVPYlpYcVNRemdKZ05cL00wSkV1K3FvQkNoN3VXMGdDQkZjOEJvVEw0bW54MSIsIm1hYyI6IjA3ZGQ0ZTk0OWJjOTk1OTdiYzE0N2YzZDUwZTE2Y2NhOWRkM2JhYzU4M2ViYTk3NzliNGM1MzY5ZTYzNGYyMWEifQ%3D%3D; cf_chl_2=c2bf5c24b0c95aa; cf_chl_rc_m=3",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "streamingcommunity.blue",
        "Referer": "https://streamingcommunity.blue/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Sec-GPC": "1",
        "TE": "trailers",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        cookies = ';'.join([
            c.strip()
            for c in str(self._get_cookies(url)).split('Set-Cookie: ')
            if len(c) > 0
        ])
        webpage = self._download_webpage(
            url, video_id, headers={
                'Cookie': cookies,
                **self._HEADERS
            }
        )
        self._video_id = self._search_regex(
            r'scws_id&quot;:(\d+)',
            webpage,
            'video_id',
            default=None
        )

        super()._real_extract(url)
