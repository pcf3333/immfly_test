from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Channel


# define view to get all channels
@csrf_exempt
def get_all_channels(request):
    # get all channels from the database
    channels = Channel.objects.all()
    channel_list = []
    # loop all channels and append a dict with the channel info to the list
    for channel in channels:
        channel_dict = {
            'id': channel.id,
            'title': channel.title,
            'language': channel.language,
            'picture': channel.picture.url if channel.picture else None,
            'subchannels': list(channel.subchannels.values_list('id', flat=True)),
            'contents': list(channel.contents.values_list('id', flat=True)),
        }
        channel_list.append(channel_dict)
    
    # return the channel list as a JSON response
    return JsonResponse({'channels': channel_list})


# define view to get a single channel
@csrf_exempt
def get_single_channel(request, channel_id):
    try:
        # get the channel with the specified channel_id
        channel = Channel.objects.get(id=channel_id)
    except Channel.DoesNotExist:
        # return a 404 error if the channel does not exist
        return JsonResponse({'error': 'Channel not found'}, status=404)

    # create a dictionary with the channel data
    channel_dict = {
        'id': channel.id,
        'title': channel.title,
        'language': channel.language,
        'picture': channel.picture.url if channel.picture else None,
        'subchannels': list(channel.subchannels.values_list('id', flat=True)),
        'contents': list(channel.contents.values_list('id', flat=True)),
    }

    # return the channel dictionary as a JSON response
    return JsonResponse(channel_dict)


# define view to get all subchannels for a channel
@csrf_exempt
def get_subchannels(request, channel_id):
    try:
        # get the channel with the specified ID
        channel = Channel.objects.get(id=channel_id)
    except Channel.DoesNotExist:
        # return a 404 error if the channel does not exist
        return JsonResponse({'error': 'Channel not found'}, status=404)

    # get all subchannels for the channel
    subchannels = channel.subchannels.all()
    subchannel_list = []
    # loop all subchannels and append a dict with the channel info to the list
    for subchannel in subchannels:
        subchannel_dict = {
            'id': subchannel.id,
            'title': subchannel.title,
            'language': subchannel.language,
            'picture': subchannel.picture.url if subchannel.picture else None,
            'contents': list(subchannel.contents.values_list('id', flat=True)),
        }
        subchannel_list.append(subchannel_dict)

    # return the subchannels list as a JSON response
    return JsonResponse({'subchannels': subchannel_list})


# define view to get all content for a channel
@csrf_exempt
def get_channel_content(request, channel_id):
    try:
        # get the channel with the specified ID
        channel = Channel.objects.get(id=channel_id)
    except Channel.DoesNotExist:
        # return a 404 error if the channel does not exist
        return JsonResponse({'error': 'Channel not found'}, status=404)

    # get all contents for the channel
    contents = channel.contents.all()
    content_list = []
    # loop all contents and append a dict with the contents info to the list
    for content in contents:
        content_dict = {
            'id': content.id,
            'title': content.title,
            'metadata': content.metadata,
            'rating': float(content.rating),
            'files': list(content.files.values_list('id', flat=True)),
        }
        content_list.append(content_dict)

    # return the contents list as a JSON response
    return JsonResponse({'contents': content_list})