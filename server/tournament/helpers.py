from django.utils           import timezone
from datetime               import timedelta
from .models                import Tournament, TournamentParticipant, TournamentMatch
from channels.layers        import get_channel_layer
from asgiref.sync           import async_to_sync
from authentication.utils   import print_red, print_green, print_yellow
from prfl.models            import Profile
from prfl.serializers       import ProfileSerializer
from django.db              import models
import time
import asyncio

def seed_players(tournament):
    participants = list(tournament.participants.all().order_by('joined_at'))
    return participants

def create_initial_matches(tournament):
    participants = seed_players(tournament)

    pairings = [
        (participants[0], participants[1]),
        (participants[2], participants[3]),
        # (participants[4], participants[5]),
        # (participants[6], participants[7]),
    ]

    for pairing in pairings:
        match = TournamentMatch.objects.create(
            tournament=tournament,
            round_number=2, #change it to 1
            player1=pairing[0],
            player2=pairing[1],
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

    for winner in winners:
        notify_winners_of_new_winner(winner, tournament, "semifinal")

    if len(winners) != 4:
        return False

    match1 = TournamentMatch.objects.create(
        tournament=tournament,
        round_number=2,
        player1=winners[0],
        player2=winners[1],
        completed=False
    )
    match2 = TournamentMatch.objects.create(
        tournament=tournament,
        round_number=2,
        player1=winners[2],
        player2=winners[3],
        completed=False
    )

    # asyncio.sleep(5)

    notify_players_of_match(match1)
    notify_players_of_match(match2)

    return True

def create_final(tournament):
    semifinals = tournament.matches.filter(round_number=2, completed=True).order_by('id')
    winners = [match.winner for match in semifinals]


    for winner in winners:
        notify_winners_of_new_winner(winner, tournament, "final")

    if len(winners) != 2:
        return False

    match = TournamentMatch.objects.create(
        tournament=tournament,
        round_number=3,
        player1=winners[0],
        player2=winners[1],
        completed=False
    )

    # asyncio.sleep(5)

    notify_players_of_match(match)

    return True

def declare_champion(tournament):
    final = tournament.matches.filter(round_number=3, completed=True).first()
    if final and final.winner:
        tournament.status = 'completed'
        tournament.save()
        notify_winners_of_new_winner(final.winner, tournament, "completed")

def notify_players_of_match(match):
    from .serializers import TournamentMatchSerializer
    channel_layer = get_channel_layer()
    match_data = TournamentMatchSerializer(match).data

    # print_yellow(f'Notifying player1: {match.player1.user.username}, player2: {match.player2.user.username}')
    # print_yellow(f'Match Data: {match_data}')

    async_to_sync(channel_layer.group_send)(
        f"user_{match.player1.user.username}",
        {"type": "send_match_info", "match_data": match_data, 'player_number': 1})

    async_to_sync(channel_layer.group_send)(
        f"user_{match.player2.user.username}",
        {"type": "send_match_info", "match_data": match_data, 'player_number': 2})

def notify_winners_of_new_winner(new_winner, tournament, round_tour):
    from .serializers           import TournamentParticipantSerializer
    channel_layer = get_channel_layer()

    winners = (
        tournament.matches.filter(winner__isnull=False)
        .values_list('winner', flat=True)
        .distinct())

    winner_participants = TournamentParticipant.objects.filter(id__in=winners)
    serialized_participants = TournamentParticipantSerializer(winner_participants, many=True).data

    for winner_participant in winner_participants:
        async_to_sync(channel_layer.group_send)(
            f"user_{winner_participant.user.username}",
            {"type": "update_winner", "winners": serialized_participants, "round": round_tour}
        )
