from datetime import datetime
from itertools import takewhile

import fbconsole


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
