from django.views.generic.base import TemplateView

from . import tasks
from .models import Feed, LogicFeedConfig


class PostView(TemplateView):
    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        config = LogicFeedConfig.objects.get()
        context['forward_to'] = config.dst_user_name

        feed_author = config.src_user_name
        feed_avatar = ('https://graph.facebook.com/{}/picture'
                       '?width=64&height=64').format(config.src_user_id)
        feed_url_base = ('https://www.facebook.com/permalink.php?'
                         'story_fbid={{}}&id={}').format(config.src_user_id)

        def feed_to_dict(feed):
            return {'avatar': feed_avatar,
                    'author': feed_author,
                    'time': feed.created_time,
                    'message': feed.text,
                    'view_url': feed_url_base.format(feed.id),
                    'forwardable': True}

        context['posts'] = map(feed_to_dict, Feed.objects.all())

        return context


def fetch(request):
    tasks.pull_new_feeds()
    return 'Done'
