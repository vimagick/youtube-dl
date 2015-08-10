# coding: utf-8
from __future__ import unicode_literals

import hashlib
import itertools

from .common import InfoExtractor, SearchInfoExtractor
from ..compat import compat_urllib_parse
from ..utils import ExtractorError


class KugouIE(InfoExtractor):
    IE_NAME = 'kugou'
    IE_DESC = '酷狗音乐'

    _VALID_URL = r'http://www\.kugou\.com/(?P<id>[0-9A-Fa-f]{32})'
    _EXTRA_QUERY_ARGS = {
        'acceptMp3': 1,
        'cmd': 4,
        'pid': 6,
    }

    _TESTS = [
        {
            'url': 'http://www.kugou.com/13DB6FDC5B0B7FFB62555F7C8A6CCE1F',
            'info_dict': {
                'id': '13DB6FDC5B0B7FFB62555F7C8A6CCE1F',
                'title': 'Me And You',
                'ext': 'mp3',
                'duration': 214,
                'url': 'http://fs.web.kugou.com/d8212b7a7c3784c7f23787cd22832add/55c69c3a/G012/M02/0C/07/rIYBAFULdvaAWeQIADRPBLdb-so866.mp3'
            }
        }
    ]

    def _real_extract(self, url):
        vid_id = self._match_id(url)
        url_query = {
            'hash': vid_id,
            'key': hashlib.md5((vid_id + 'kgcloud').encode()).hexdigest(),
        }
        url_query.update(self._EXTRA_QUERY_ARGS)
        result_url = 'http://trackercdn.kugou.com/i/?' + compat_urllib_parse.urlencode(url_query)

        data = self._download_json(result_url, video_id=vid_id)

        if data['status'] != 1:
            raise ExtractorError('[kugou] No such video', expected=True)

        return {
            'id': vid_id,
            'url': data['url'],
            'ext': data['extName'],
            'duration': data['timeLength'],
        }


class KugouSearchIE(SearchInfoExtractor):
    IE_NAME = 'kugou:search'
    IE_DESC = '酷狗搜索'

    _SEARCH_KEY = 'kgsearch'
    _MAX_RESULTS = float('inf')
    _EXTRA_QUERY_ARGS = {
        'cmd': 100,
    }

    def _get_n_results(self, query, n):
        videos = []
        limit = n

        for pagenum in itertools.count(1):
            url_query = {
                'keyword': query.encode('utf-8'),
                'page': pagenum,
                'pagesize': 10,
            }
            url_query.update(self._EXTRA_QUERY_ARGS)
            result_url = 'http://lib9.service.kugou.com/websearch/index.php?' + compat_urllib_parse.urlencode(url_query)
            data = self._download_json(
                result_url, video_id='query "%s"' % query,
                note='Downloading page %s' % pagenum,
                errnote='Unable to download API page')

            if not (data['status'] == 1 and data['data']['songs']):
                raise ExtractorError('[kugou] No video results', expected=True)

            new_videos = [
                {
                    '_type': 'url_transparent',
                    'url': 'http://www.kugou.com/' + song['hash'],
                    'ie_key': 'Kugou',
                    'title': song['songname'],
                    'creator': song['singername'],
                    'uploader': 'kugou',
                } for song in data['data']['songs']
            ]

            videos += new_videos
            if not new_videos or len(videos) >= limit:
                break

        if len(videos) > n:
            videos = videos[:n]

        return self.playlist_result(videos, query)

