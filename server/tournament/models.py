from django.db 					import models
from django.utils.translation 	import gettext_lazy as _
from prfl.models 		        import Profile
import uuid

class Tournament(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='tournaments_created')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='tournaments_participated')
    alias = models.CharField(max_length=255)
    joined_at = models.DateTimeField(auto_now_add=True)
    isDisconnect = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tournament', 'user', 'alias')

    def __str__(self):
        return f"{self.user.username}"

class TournamentMatch(models.Model):
    ROUND_CHOICES = [
        (1, 'Quarterfinal'),
        (2, 'Semifinal'),
        (3, 'Final'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    round_number = models.IntegerField(choices=ROUND_CHOICES)
    player1 = models.ForeignKey(TournamentParticipant, on_delete=models.CASCADE, related_name='matches_as_player1', null=True, blank=True)
    player2 = models.ForeignKey(TournamentParticipant, on_delete=models.CASCADE, related_name='matches_as_player2', null=True, blank=True)
    winner = models.ForeignKey(TournamentParticipant, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    number_player = models.IntegerField(default=2)
    completed = models.BooleanField(default=False)
    interupted = models.BooleanField(default=False)
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)
    
    def __str__(self):
        p1 = self.player1.user.username
        p2 = self.player2.user.username
        return f"Round {self.round_number}: {p1} vs {p2}"

class TournamentMatchHistory(models.Model):
    tournamentMatch = models.OneToOneField(TournamentMatch, null=True, blank=True, on_delete=models.SET_NULL, related_name='tournamentMatchHistory')
    winner = models.ForeignKey(TournamentParticipant, related_name='tournamentWinner', on_delete=models.CASCADE)
    loser = models.ForeignKey(TournamentParticipant, related_name='tournamentLoser', on_delete=models.CASCADE)
    winner_score = models.IntegerField()
    loser_score = models.IntegerField()
    ended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.winner} defeated {self.loser}'
