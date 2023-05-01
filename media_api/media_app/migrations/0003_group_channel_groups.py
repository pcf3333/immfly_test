# Generated by Django 4.2 on 2023-04-29 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_app', '0002_remove_channel_subchannels_channel_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('channels', models.ManyToManyField(related_name='group_channels', to='media_app.channel')),
            ],
        ),
        migrations.AddField(
            model_name='channel',
            name='groups',
            field=models.ManyToManyField(related_name='channel_groups', to='media_app.group'),
        ),
    ]