import json
import re

from .common import InfoExtractor


class StreamingCommunityIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?scws\.work/master/(?P<id>[0-9]+).*'

    _TESTS = [{
        'url': 'https://streamingcommunity.blue/watch/5471',
        'md5': 'TODO: md5 sum of the first 10241 bytes of the video file (use --test)',
        'info_dict': {
            'id': '5471',
            'ext': 'mp4',
            'title': 'Adventure Time S1:E1 Ep. 01-02 | La morte dei morti dolce',
            'thumbnail': r're:^https?://.*\.jpg$',
            # TODO more properties, either as:
            # * A value
            # * MD5 checksum; start the string with md5:
            # * A regular expression; start the string with re:
            # * Any Python type, e.g. int or float
        }
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        work_url = f'https://scws.work/videos/{video_id}'
        data = json.loads(
            self._download_webpage(work_url, video_id)
        )

        # TODO more code goes here, for example ...
        # title = self._html_search_regex(r'<h1>(.+?)</h1>', webpage, 'title')

        match = re.match(r'.*type=(\w+)&rendition=(.*?)&.*', url)
        typ, resolution = match[1], match[2]
        cdn = data['cdn']
        fragments = []
        next_cdn_proxy_index = data['proxy_index']
        num_cdn_proxies = len(cdn['proxies'])

        for f in webpage.split('\n'):
            if f[0] == '#':
                continue

            proxy_num = cdn['proxies'][next_cdn_proxy_index % num_cdn_proxies]['number']
            next_cdn_proxy_index += 1

            frag_url = f'https://sc-{cdn["type"]}{cdn["number"]}-{proxy_num:02d}.{data["host"]}/hls/{data["storage"]["number"]}/{data["folder_id"]}/{typ}/{resolution}/{f}'

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
