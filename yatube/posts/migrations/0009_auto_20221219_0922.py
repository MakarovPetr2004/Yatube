# Generated by Django 2.2.19 on 2022-12-19 09:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20221218_1642'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-created',), 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
        migrations.RemoveField(
            model_name='post',
            name='pub_date',
        ),
        migrations.AddField(
            model_name='post',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
    ]
