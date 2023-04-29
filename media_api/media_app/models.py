from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Avg


class File(models.Model):
    file = models.FileField(upload_to='content_files/')

class Content(models.Model):
    title = models.CharField(max_length=255)
    metadata = models.JSONField()
    rating = models.DecimalField(max_digits=3,decimal_places=1)
    files = models.ManyToManyField('File', blank=True)

class Channel(models.Model):
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='channel_pictures/')
    contents = models.ManyToManyField(Content, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subchannels')

    # Cache for saving channel ratings
    _ratings_cache = {}


    def clean(self):
        # Throw a ValidationError if the channel has contents and subchannels at the same time
        if self.subchannels.exists() and self.contents.exists():
            raise ValidationError('A channel cannot have both subchannels and contents.')

        # Throw a ValidationError if the channel does not have contents nor subchannels
        if not self.subchannels.exists() and not self.contents.exists():
            raise ValidationError('A channel must have at least one subchannel or content.')


    def save(self, *args, **kwargs):
        # This is important because if the object has not been created before, you cannot check the 
        # ManyToManyField, as it needs an ID.
        if self.pk:
            self.clean()
        super().save(*args, **kwargs) 


    def calculate_rating(self):
        # If the channel exists in cache, just return it's value
        if self in self._ratings_cache:
            return self._ratings_cache[self.id]
        
        if self.subchannels.exists():
            # In case there is any invalid channel, we throw None, however this case should not be possible
            if self.contents.exists():
                self._ratings_cache[self.id] = None
                return None
        
            # Looping recursively all the subchannels and adding the ratings to a list
            subchannels_ratings = []
            for subchannel in self.subchannels.all():
                if subchannel.calculate_rating() is not None:
                    subchannels_ratings.append(subchannel.calculate_rating())

            # Averaging all the ratings
            if subchannels_ratings:
                rating = float(sum(subchannels_ratings) / len(subchannels_ratings))
            else:
                rating = None
        else:
            # If the channel does not have subchannels, calculate the average rating of its contents (if any)
            contents = self.contents.filter(rating__isnull=False)
            if contents.exists():
                rating = float(contents.aggregate(avg_rating=Avg('rating'))['avg_rating'])
            else:
                rating = None
                
        # Save the rating in the cahce and return it
        self._ratings_cache[self.id] = rating
        return rating
        