# from django.urls import path
# from .consumer import *

# websocket_urlpatterns = [
#     path('ws/notifications/', NotificationConsumer.as_asgi()),
# ]

from django.urls import re_path

from .consumer import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<plant_id>\d+)/$', NotificationConsumer.as_asgi()),
]
