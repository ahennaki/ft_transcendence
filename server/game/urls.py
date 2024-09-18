from django.urls            import path, include
from rest_framework.routers import DefaultRouter
from .views                 import *

app_name = 'game'

urlpatterns = [
    # path('join/', JoinQueueView.as_view(), name='join_queue'),
    path('match/<int:match_id>/', MatchStatusView.as_view(), name='match_status'),
    path('match_end/', EndMatchView.as_view(), name='match_end'),
    path('setting/', SettingUpdateView.as_view(), name='setting'),
    path('settings/<int:profile_id>/', ProfileSettingsView.as_view(), name='profile-settings'),
]
