from django.utils           import timezone
from datetime               import timedelta
from .models                import Tournament, TournamentParticipant, TournamentMatch
from channels.layers        import get_channel_layer
from asgiref.sync           import async_to_sync
from authentication.utils   import print_red, print_green, print_yellow

def seed_players(tournament):
    participants = list(tournament.participants.all().order_by('joined_at'))
    return participants

def create_initial_matches(tournament):
    participants = seed_players(tournament)

    pairings = [
        (participants[0], participants[1]),
        (participants[2], participants[3]),
        (participants[4], participants[5]),
        (participants[6], participants[7]),
    ]
    # scheduled_time = timezone.now() + timedelta(hours=1)

    for pairing in pairings:
        match = TournamentMatch.objects.create(
            tournament=tournament,
            round_number=1,
            player1=pairing[0],
            player2=pairing[1],
            # scheduled_time=scheduled_time,
            completed=False
        )
        notify_players_of_match(match)

def progress_tournament(tournament):
    current_round = None
    if tournament.status == 'ongoing':
        incomplete_matches = tournament.matches.filter(completed=False).order_by('-round_number')
        if incomplete_matches.exists():
            current_round = incomplete_matches.first().round_number
        else:
            last_completed_round = tournament.matches.aggregate(models.Max('round_number'))['round_number__max']
            current_round = last_completed_round

    if current_round is None:
        return

    if current_round == 1:
        semifinals = create_semifinals(tournament)
        if semifinals:
            return

    elif current_round == 2:
        final = create_final(tournament)
        if final:
            return

    elif current_round == 3:
        declare_champion(tournament)

def create_semifinals(tournament):
    quarterfinals = tournament.matches.filter(round_number=1, completed=True).order_by('id')
    winners = [match.winner for match in quarterfinals]

    if len(winners) != 4:
        return False

    # scheduled_time = timezone.now() + timedelta(hours=2)

    match1 = Match.objects.create(
        tournament=tournament,
        round_number=2,
        player1=winners[0],
        player2=winners[1],
        # scheduled_time=scheduled_time,
        completed=False
    )
    match2 = Match.objects.create(
        tournament=tournament,
        round_number=2,
        player1=winners[2],
        player2=winners[3],
        # scheduled_time=scheduled_time,
        completed=False
    )

    notify_players_of_match(match1)
    notify_players_of_match(match2)

    return True

def create_final(tournament):
    semifinals = tournament.matches.filter(round_number=2, completed=True).order_by('id')
    winners = [match.winner for match in semifinals]

    if len(winners) != 2:
        return False

    # scheduled_time = timezone.now() + timedelta(hours=3)

    match = Match.objects.create(
        tournament=tournament,
        round_number=3,
        player1=winners[0],
        player2=winners[1],
        # scheduled_time=scheduled_time,
        completed=False
    )

    notify_players_of_match(match)

    return True

def declare_champion(tournament):
    final = tournament.matches.filter(round_number=3, completed=True).first()
    if final and final.winner:
        tournament.status = 'completed'
        tournament.save()

def notify_players_of_match(match):
    from .serializers import MatchSerializer
    channel_layer = get_channel_layer()
    match_data = MatchSerializer(match).data

    print_yellow(f'Notifying player1: {match.player1.user.username}, player2: {match.player2.user.username}')
    print_yellow(f'Match Data: {match_data}')

    async_to_sync(channel_layer.group_send)(
        f"user_{match.player1.user.username}",
        {"type": "send_match_info", "match_data": match_data, 'player_number': 1})

    async_to_sync(channel_layer.group_send)(
        f"user_{match.player2.user.username}",
        {"type": "send_match_info", "match_data": match_data, 'player_number': 2})
