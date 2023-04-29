from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Channel, Content

# When a content is saved (added or edited) or deleted, all the parent channels need to 
# recalculate the rating in the cache, so we delete them from there
@receiver([post_save, post_delete, m2m_changed], sender=Content)
def clear_channel_cache_on_content_change(sender, instance, **kwargs):
    # We need to find all the channels that have this content
    channels = Channel.objects.filter(contents=instance)
    for channel in channels:
        # Looping all the parent channels until the top channel and removing the cached rating
        while channel is not None:
            channel._ratings_cache.pop(channel.id, None)
            channel = channel.parent
    

# When a channel is saved (added or edited) or deleted, all the parent channels need to 
# recalculate the rating in the cache, so we delete them from there
@receiver([post_save, post_delete, m2m_changed], sender=Channel)
def clear_channel_cache_on_channel_change(sender, instance, **kwargs):
    channel = instance
    # Looping all the parent channels until the top channel and removing the cached rating
    while channel is not None:
        channel._ratings_cache.pop(channel.id, None)
        channel = channel.parent