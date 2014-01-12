from django.contrib import admin

from singleton_models.admin import SingletonModelAdmin

from .models import Post, Image, Font, LastUpdate, Feed, LogicFeedConfig


class CreatedTimeAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_time'


admin.site.register(Post, CreatedTimeAdmin)
admin.site.register(Image)
admin.site.register(Font)
admin.site.register(LastUpdate, SingletonModelAdmin)
admin.site.register(Feed, CreatedTimeAdmin)
admin.site.register(LogicFeedConfig, SingletonModelAdmin)