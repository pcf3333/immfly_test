# Generated by Django 4.2 on 2023-04-26 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='content_files/')),
            ],
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('metadata', models.JSONField()),
                ('rating', models.DecimalField(decimal_places=1, max_digits=3)),
                ('files', models.ManyToManyField(blank=True, to='media_app.file')),
            ],
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('language', models.CharField(max_length=255)),
                ('picture', models.ImageField(upload_to='channel_pictures/')),
                ('contents', models.ManyToManyField(blank=True, to='media_app.content')),
                ('subchannels', models.ManyToManyField(blank=True, to='media_app.channel')),
            ],
        ),
    ]
