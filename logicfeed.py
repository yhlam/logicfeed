from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from itertools import takewhile
import json
import time
import re

import fbconsole


__all__ = ['get_posts', 'get_post_stream']


def _get_fb_data(url):
    fbconsole.AUTH_SCOPE = ['read_stream']
    fbconsole.authenticate_via_cookie()
    return fbconsole.iter_pages(fbconsole.get(url))


def _get_post_created_time(post):
    created_time_str = post['created_time']
    created_time = datetime.strptime(created_time_str, '%Y-%m-%dT%H:%M:%S+0000')
    return created_time


def get_posts(userid, since):
    def is_post_after(post):
        created_time = _get_post_created_time(post)
        return created_time > since

    def is_status(post):
        return post['type'] == 'status'

    url = '/' + userid + '/posts'
    return list(filter(is_status, takewhile(is_post_after, _get_fb_data(url))))


def get_post_stream(userid, since=None, update_interval=60):
    last_created_time = datetime.now() if since is None else since
    while True:
        posts = get_posts(userid, last_created_time)
        if posts:
            last_created_time = _get_post_created_time(posts[0])
            for post in posts:
                yield post
        time.sleep(update_interval)


if __name__ == '__main__':
    def get_arg_parser():
        def starttime(timestr):
            formats = [(r'^\d{4}$', '%Y'),
                       (r'^\d{4}-\d{2}$', '%Y-%m'),
                       (r'^\d{2}-\d{2}$', '%m-%d'),
                       (r'^\d{4}-\d{2}-\d{2}$', '%Y-%m-%d'),
                       (r'^\d{4}-\d{2}-\d{2}T\d{2}$', '%Y-%m-%dT%H'),
                       (r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$', '%Y-%m-%dT%H:%M'),
                       (r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$', '%Y-%m-%dT%H:%M:%S')]
            for regex, fmt in formats:
                if re.match(regex, timestr):
                    return datetime.strptime(timestr, fmt)
            raise ArgumentTypeError('{} is not a valid start time'.format(timestr))

        parser = ArgumentParser(description='Display the post stream of a facebook user')
        parser.add_argument('user_id', type=str, help='ID of the facebook user')
        parser.add_argument('-t', type=int, help='Update time interval of the stream in seconds (default: 60s)', default=60, dest='interval')
        parser.add_argument('-s', type=starttime, help='Start time of the stream (default: now)', default=None, dest='start')
        return parser

    parser = get_arg_parser()
    args = parser.parse_args()
    for post in get_post_stream(args.user_id, args.start, args.interval):
        print(json.dumps(post, sort_keys=True, indent=4, separators=(',', ':')))
