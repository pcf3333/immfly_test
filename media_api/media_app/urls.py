from django.urls import path
from . import views

urlpatterns = [
    # API Urls
    path('api/get_all_channels/', views.get_all_channels, name='get_all_channels'),
    path('api/get_single_channel/<int:channel_id>/', views.get_single_channel, name='get_single_channel'),
    path('api/get_subchannels/<int:channel_id>/', views.get_subchannels, name='get_subchannels'),
    path('api/get_channel_content/<int:channel_id>/', views.get_channel_content, name='get_channel_content'),
]