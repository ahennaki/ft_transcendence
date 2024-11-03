from channels.db                import database_sync_to_async
from .models                    import MatchHistory, Match
from prfl.models                import Profile
from prfl.serializers           import ProfileSerializer
from authentication.utils       import print_red, print_green, print_yellow
from tournament.models          import TournamentMatch, TournamentMatchHistory

async def end_game(consumer, isDisconnect):
    print_green(f'end of the game!')
    wn, ln, winner, loser, ws, ls = determine_winner_loser(consumer, isDisconnect)
    print_green(f'winner: {winner}')

    await save_match_history(consumer, winner, loser, ws, ls)
    await set_badge(winner, 1)
    await set_badge(loser, 0)

    winner_profile = await get_profile_data(winner)
    loser_profile = await get_profile_data(loser)

    data = {"type": "end_game", "match_id": consumer.match_id, "winner": wn,
        "loser": ln, "score": f'{ws}-{ls}',
        "winner_profile": winner_profile,
        "loser_profile": loser_profile,
        "player1_score": consumer.score1,
        "player2_score": consumer.score2,
        "match_round": 0
    }

    await consumer.channel_layer.group_send(
        f"user_{consumer.player1_username}",
        {"type": "end_game", "data": data}
    )
    await consumer.channel_layer.group_send(
        f"user_{consumer.player2_username}",
        {"type": "end_game", "data": data}
    )

@database_sync_to_async
def get_profile_data(player):
    serializer = ProfileSerializer(player)  
    return serializer.data

@database_sync_to_async
def set_badge(player, isWinner):
    profile = Profile.objects.get(username=player)
    if isWinner:
        profile.rank += 50
        profile.wins += 1
        # print_yellow(f'player data: {profile.rank}')
    else:
        profile.loses += 1
    if 0 < profile.rank <= 200:
        profile.badge = 'BRONZE'
    elif 200 < profile.rank <= 400:
        profile.badge = 'SILVER'
    elif 400 < profile.rank <= 600:
        profile.badge = 'GOLD'
    elif 600 < profile.rank <= 800:
        profile.badge = 'PLATINUM'
    elif 800 < profile.rank <= 1000:
        profile.badge = 'DIAMOND'
    elif 1000 < profile.rank <= 1200:
        profile.badge = 'HEROIC'
    elif 1200 < profile.rank:
        profile.badge = 'GRAND_MASTER'
    profile.save()

def determine_winner_loser(consumer, isDisconnect):
    if not isDisconnect:
        if consumer.score1 > consumer.score2:
            if consumer.score1 > 10:
                consumer.score1 = 10
            return 1, 2, consumer.match.player1, consumer.match.player2, consumer.score1, consumer.score2
        elif consumer.score2 > consumer.score1:
            if consumer.score2 > 10:
                consumer.score2 = 10
            return 2, 1, consumer.match.player2, consumer.match.player1, consumer.score2, consumer.score1
    else:
        if consumer.user.username == consumer.player2_username:
            consumer.score1 = 10
            return 1, 2, consumer.match.player1, consumer.match.player2, consumer.score1, consumer.score2
        elif consumer.user.username == consumer.player1_username:
            consumer.score2 = 10
            return 2, 1, consumer.match.player2, consumer.match.player1, consumer.score2, consumer.score1 

@database_sync_to_async
def save_match_history(consumer, winner, loser, winner_score, loser_score):
    match = Match.objects.get(id=consumer.match_id)
    match.status = 'finished'
    match.save()

    MatchHistory.objects.create(
        match=match,
        winner=winner,
        loser=loser,
        winner_score=winner_score,
        loser_score=loser_score
    )
