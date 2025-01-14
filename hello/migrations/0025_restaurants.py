# Generated by Django 4.1.5 on 2023-01-11 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0024_diets'),
    ]

    operations = [
        migrations.CreateModel(
            name='restaurants',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('url', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True))
            ],
        )
    ]