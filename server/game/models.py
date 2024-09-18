from django.db      import models
from prfl.models    import Profile

class Match(models.Model):
    player1 = models.ForeignKey(Profile, related_name='player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(Profile, related_name='player2', on_delete=models.CASCADE)
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='waiting')

    def __str__(self):
        return f'{self.player1} vs {self.player2}'

class MatchHistory(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='history')
    winner = models.ForeignKey(Profile, related_name='winner', on_delete=models.CASCADE)
    loser = models.ForeignKey(Profile, related_name='loser', on_delete=models.CASCADE)
    winner_score = models.IntegerField()
    loser_score = models.IntegerField()
    ended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.winner} defeated {self.loser}'

class PlayerQueue(models.Model):
    player = models.ForeignKey(Profile, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

class Setting(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='settings')
    mapname = models.CharField(max_length=100, default='default')
    ballcolor = models.CharField(max_length=100, default='green')
    score = models.CharField(max_length=100, default='Five')
    botlevel = models.FloatField(default=0.1)

    def __str__(self):
        return self.mapname

# class GameInvitation(models.Model):
#     sender = models.ForeignKey(Profile, related_name='sent_invitations', on_delete=models.CASCADE)
#     receiver = models.ForeignKey(Profile, related_name='received_invitations', on_delete=models.CASCADE)
#     status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Invitation from {self.sender} to {self.receiver}"
