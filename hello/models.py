from datetime import datetime
from django.db import models

class Question(models.Model):
    question = models.CharField(max_length=140)
    context = models.TextField(null=True, blank=True)
    answer = models.TextField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField("date created", default=datetime.now, null=True)
    ask_count = models.IntegerField(default=1)
    #audio_src_url = models.CharField(default="", max_length=255, null=True, blank=True)

class user_avatars(models.Model):
    created_at = models.DateTimeField("date created", default=datetime.now, null=True)
    avatar_id = models.IntegerField(null=True)
    user_id = models.IntegerField(null=True)

class avatars(models.Model):
    created_at = models.DateTimeField("date created", default=datetime.now, null=True)
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    visibility = models.TextField(null=True, blank=True)
    url_path = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)

class files(models.Model):
    created_at = models.DateTimeField("date created", default=datetime.now, null=True)
    avatar_id = models.IntegerField(null=True)
    file_url = models.CharField(default="", max_length=255, null=True, blank=True)