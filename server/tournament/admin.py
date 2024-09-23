from django.contrib import admin
from .models 		import Tournament, TournamentParticipant, Match

admin.site.register(Tournament)
admin.site.register(TournamentParticipant)
admin.site.register(Match)
