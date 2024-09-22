from django.urls 	import path
from .views 		import CreateTournamentView, JoinTournamentView, ListTournamentsView, UpdateMatchView

urlpatterns = [
    path('create/', CreateTournamentView.as_view(), name='create-tournament'),
    path('join/', JoinTournamentView.as_view(), name='join-tournament'),
    path('list/', ListTournamentsView.as_view(), name='list-tournaments'),
    path('matches/<uuid:pk>/update/', UpdateMatchView.as_view(), name='update-match'),
]
