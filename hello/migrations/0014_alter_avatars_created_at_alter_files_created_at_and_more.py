# Generated by Django 4.1.5 on 2023-01-11 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0013_avatars_files_user_avatars_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatars',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='files',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='user_avatars',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='date created'),
        ),
    ]
