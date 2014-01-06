from django.contrib import auth
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone

from singleton_models.models import SingletonModel


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


@python_2_unicode_compatible
class Image(models.Model):
    file = models.ImageField(upload_to='background')
    margin_bottom = models.PositiveSmallIntegerField()
    wrap_width = models.PositiveSmallIntegerField()


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
