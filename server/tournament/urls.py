from django.urls 	import path
from .views 		import *

urlpatterns = [
    path('names/', TournamentNameListView.as_view(), name='tournament-names'),
    path('check-alias/', AliasAvailabilityCheckView.as_view(), name='check-alias'),
    path('check-name/', TournamentNameCheckView.as_view(), name='check-name'),
    path('create/', CreateTournamentView.as_view(), name='create-tournament'),
    path('join/', JoinTournamentView.as_view(), name='join-tournament'),
    path('list/', ListTournamentsView.as_view(), name='list-tournaments'),
    path('matches/<uuid:pk>/update/', UpdateMatchView.as_view(), name='update-match'),
]
