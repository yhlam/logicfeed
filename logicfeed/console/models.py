from django.contrib import auth
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone

from singleton_models.models import SingletonModel

from .meme import draw_meme

User = auth.get_user_model()


class LastUpdateManager(models.Manager):
    def get_timestamp(self):
        last_update = self.get()
        return last_update.timestamp

    def get_timestamp_and_update(self):
        last_update = self.get()
        timestamp, last_update.timestamp = last_update.timestamp, timezone.now()
        last_update.save()
        return timestamp


@python_2_unicode_compatible
class Feed(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    text = models.TextField()
    created_time = models.DateTimeField()

    def __str__(self):
        return 'Feed {{id: {}, text: {}, created_time: {}}}'.format(self.id, self.text, self.created_time)

    def generate_meme(self, image, fill_color, border_color, border_size,
                      font_path, font_size=None, spacing=None):
        font_size = font_size or image.font_size
        spacing = image.spacing if spacing is None else spacing
        return draw_meme(self.text, image.file.path, fill_color, border_color,
                         border_size, font_path, font_size, spacing,
                         image.margin_bottom, image.wrap_width)


@python_2_unicode_compatible
class Image(models.Model):
    file = models.ImageField(upload_to='background')
    margin_bottom = models.PositiveSmallIntegerField()
    wrap_width = models.PositiveSmallIntegerField()

    @property
    def font_size(self):
        return self.file.height // 10

    @property
    def spacing(self):
        return self.font_size // 2


@python_2_unicode_compatible
class Font(models.Model):
    name = models.CharField(max_length=64)
    css_font_family = models.CharField(max_length=138)
    path = models.CharField(max_length=256)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class LastUpdate(SingletonModel):
    timestamp = models.DateTimeField(auto_now_add=True)
    timestamp.editable = True

    objects = LastUpdateManager()

    def __str__(self):
        return "Last updated at {:%Y-%m-%d %H:%M:%S}".format(self.timestamp)


@python_2_unicode_compatible
class Post(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    author = models.ForeignKey(User)
    text = models.TextField()
    font = models.ForeignKey(Font)
    font_size = models.PositiveSmallIntegerField()
    fill_color = models.CharField(max_length=6)
    border_color = models.CharField(max_length=6)
    border_width = models.PositiveSmallIntegerField()
    margin_bottom = models.PositiveSmallIntegerField()
    wrap_width = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to='post')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Post {{id: {}, text: {}, created_time: {}, author: {}}}'.format(
            self.id, self.text, self.created_time, self.author)


@python_2_unicode_compatible
class LogicFeedConfig(SingletonModel):
    src_user_id = models.BigIntegerField()
    src_user_name = models.CharField(max_length=128)
    dst_user_id = models.BigIntegerField()
    dst_user_name = models.CharField(max_length=128)
    avatar = models.ImageField(upload_to='config')
    email_subject = models.CharField(max_length=128)
    email_sender = models.EmailField()
    fb_cookies_c_user = models.CharField(max_length=128)
    fb_cookies_xs = models.CharField(max_length=128)

    def __str__(self):
        return "{} => {}".format(self.src_user_name, self.dst_user_name)
