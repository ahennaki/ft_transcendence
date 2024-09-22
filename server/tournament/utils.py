from django.utils import timezone
from datetime import timedelta
from .models import Tournament, TournamentParticipant, Match

def seed_players(tournament):
    participants = list(tournament.participants.all())
    # participants.sort(key=lambda p: p.user.profile.rank, reverse=True)
    return participants

def create_initial_matches(tournament):
    participants = seed_players(tournament)
    pairings = [
        (participants[0], participants[7]),
        (participants[3], participants[4]),
        (participants[1], participants[6]),
        (participants[2], participants[5]),
    ]
    scheduled_time = timezone.now() + timedelta(hours=1)

    for pairing in pairings:
        Match.objects.create(
            tournament=tournament,
            round_number=1,
            player1=pairing[0],
            player2=pairing[1],
            scheduled_time=scheduled_time,
            completed=False
        )

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

    scheduled_time = timezone.now() + timedelta(hours=2)

    semifinal1 = Match.objects.create(
        tournament=tournament,
        round_number=2,
        player1=winners[0],
        player2=winners[1],
        scheduled_time=scheduled_time,
        completed=False
    )
    semifinal2 = Match.objects.create(
        tournament=tournament,
        round_number=2,
        player1=winners[2],
        player2=winners[3],
        scheduled_time=scheduled_time,
        completed=False
    )

    return True

def create_final(tournament):
    semifinals = tournament.matches.filter(round_number=2, completed=True).order_by('id')
    winners = [match.winner for match in semifinals]

    if len(winners) != 2:
        return False

    scheduled_time = timezone.now() + timedelta(hours=3)

    final = Match.objects.create(
        tournament=tournament,
        round_number=3,
        player1=winners[0],
        player2=winners[1],
        scheduled_time=scheduled_time,
        completed=False
    )

    return True

def declare_champion(tournament):
    final = tournament.matches.filter(round_number=3, completed=True).first()
    if final and final.winner:
        tournament.status = 'completed'
        tournament.save()

