from django.core.management.base import BaseCommand
from media_app.models import Channel
from media_app import models
import csv

class Command(BaseCommand):
    help = 'Calculates the ratings of every channel and exports them in a CSV file sorted by rating'

    def handle(self, *args, **options):
        channels = Channel.objects.all()
        rows = []
        for channel in channels:
            avg_rating = channel.calculate_rating()
            if avg_rating is not None:
                rows.append([channel.title, avg_rating])
        sorted_rows = sorted(rows, key=lambda x: x[1], reverse=True)
        with open('channel_ratings.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Channel Title', 'Average Rating'])
            for row in sorted_rows:
                writer.writerow(row)
        self.stdout.write(self.style.SUCCESS('Successfully exported!'))