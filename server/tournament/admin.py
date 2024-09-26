from django.contrib import admin
from .models 		import Tournament, TournamentParticipant, TournamentMatch

admin.site.register(Tournament)
admin.site.register(TournamentParticipant)
admin.site.register(TournamentMatch)
