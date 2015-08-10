#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from bottle import get, request, redirect, response, run
from youtube_dl import YoutubeDL
import os
import time

__version__ = '0.0.1'


@get('/')
def index():
    response.headers['Content-Type'] = 'text/plain'
    return 'Foobar Music Search (version: {})'.format(__version__)


@get('/info')
def info():
    return {
        'homepage': 'http://music.foobar.site/',
        'version': __version__,
        'timestamp': time.time(),
        'endpoints': {
            'kugou': '/kugou/<keyword>',
            'kuwo': '/kuwo/<keyword>',
            'qqmusic': '/qqmusic/<keyword>',
        }
    }


@get('/<search>/<keyword>')
def search(search, keyword):
    try:
        max_results = int(request.query.max_results or 10)
        page= int(request.query.page or 1)

        lookup = {
            'kugou': 'kgsearch',
            'kuwo': 'kwsearch',
            'qqmusic': 'qmsearch',
        }

        query = '{}{}:{}'.format(lookup.get(search, 'qmsearch'), max_results, keyword)
        result = YDL.extract_info(query, download=False)

        return {
            '_items': [
                {
                    'id': i.get('id'),
                    'url': i.get('url'),
                    'title': i.get('title'),
                    'creator': i.get('creator'),
                    'uploader': i.get('uploader'),
                    'ext': i.get('ext'),
                    'duration': i.get('duration'),
                } for i in result['entries']
            ],
            '_meta': {
                'max_results': max_results,
            }
        }
    except Exception as ex:
        return {
            '_error': {
                'code': 500,
                'message': str(ex),
            },
            '_status': 'ERR'
        }


if __name__ == '__main__':
    YDL = YoutubeDL({'format': 'mp3'})
    host = os.getenv('HOST', '127.0.0.1')
    port = os.getenv('PORT', '80')
    workers = int(os.getenv('WORKERS', 1))
    run(host=host, port=port, server='gunicorn', workers=workers)

