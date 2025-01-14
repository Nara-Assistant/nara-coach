# Generated by Django 4.1.5 on 2023-01-11 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0012_remove_question_real_answer'),
    ]

    operations = [
        migrations.CreateModel(
            name='avatars',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('visibility', models.TextField(blank=True, null=True)),
                ('url_path', models.TextField(blank=True, null=True)),
                ('status', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('avatar_id', models.IntegerField(null=True)),
                ('file_url', models.CharField(blank=True, default='', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='user_avatars',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('avatar_id', models.IntegerField(null=True)),
                ('user_id', models.IntegerField(null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='question',
            name='audio_src_url',
        ),
    ]
