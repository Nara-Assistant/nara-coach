from datetime import datetime
from django.db import models

class Question(models.Model):
    question = models.CharField(max_length=140)
    context = models.TextField(null=True, blank=True)
    answer = models.TextField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField("date created", auto_now_add=True, null=True)
    ask_count = models.IntegerField(default=1)
    #audio_src_url = models.CharField(default="", max_length=255, null=True, blank=True)

class user_avatars(models.Model):
    created_at = models.DateTimeField("date created", auto_now_add=True, null=True)
    avatar_id = models.IntegerField(null=True)
    user_id = models.TextField(null=True, blank=True)

class avatars(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    created_at = models.DateTimeField("date created", auto_now_add=True, null=True)
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    visibility = models.TextField(null=True, blank=True)
    url_path = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)

class diets(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    created_at = models.DateTimeField("date created", auto_now_add=True, null=True)
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    visibility = models.TextField(null=True, blank=True)
    diet_type = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)

class files(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    created_at = models.DateTimeField("date created", auto_now_add=True, null=True)
    avatar_id = models.IntegerField(null=True)
    file_url = models.CharField(default="", max_length=255, null=True, blank=True)
    file_type = models.CharField(default="TRAINING", max_length=255, null=True, blank=True)

class PresetQuestions(models.Model):
    created_at = models.DateTimeField("date created", auto_now_add=True, null=True)
    avatar_id = models.IntegerField(null=True)
    question = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)

class Prompts(models.Model):
    created_at = models.DateTimeField("date created", auto_now_add=True, null=True)
    avatar_id = models.IntegerField(null=True)
    value = models.TextField(null=True, blank=True)

class Users(models.Model):
    id = models.CharField(default="", max_length=255, primary_key=True)
    aud = models.CharField(default="", max_length=255, null=True, blank=True)
    role = models.CharField(default="TRAINING", max_length=255, null=True, blank=True)

    class Meta:
        db_table = '"auth"."users"'

class Sessions(models.Model):
    id = models.CharField(default="", max_length=255, primary_key=True)
    user_id = models.CharField(default="", max_length=255, null=True, blank=True)

    class Meta:
        db_table = '"auth"."sessions"'


class TrainingQueue(models.Model):
    avatar_id = models.IntegerField(null=True)
    status = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'hello_training_queue'