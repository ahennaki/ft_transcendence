from django.contrib 	import admin
from .models 			import Match, Setting, MatchHistory

admin.site.register(Match)
admin.site.register(MatchHistory)
admin.site.register(Setting)
