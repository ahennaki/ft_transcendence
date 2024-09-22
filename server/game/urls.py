from django.urls            import path, include
from rest_framework.routers import DefaultRouter
from .views                 import *

app_name = 'game'

urlpatterns = [
    # path('join/', JoinQueueView.as_view(), name='join_queue'),
    path('match/<int:match_id>/', MatchStatusView.as_view(), name='match_status'),
    path('match-history/<str:username>/', PlayerMatchHistoryView.as_view(), name='player-match-history'),
    path('setting/', SettingUpdateView.as_view(), name='setting'),
    path('settings/<int:profile_id>/', ProfileSettingsView.as_view(), name='profile-settings'),
    path('player/<int:profile_id>/', ProfileIdDataView.as_view(), name='profile-player'),
]
