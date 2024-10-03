from channels.db                import database_sync_to_async
from .models                    import MatchHistory, Match
from prfl.models                import Profile
from prfl.serializers           import ProfileSerializer
from authentication.utils       import print_red, print_green, print_yellow
from tournament.models          import TournamentMatch

async def end_game(consumer, isDisconnect):
    wn, ln, winner, loser, ws, ls = determine_winner_loser(consumer, isDisconnect)

    print_green(f'end of the game! winner: {winner}')
    if consumer.isTournament:
        await save_tounament_match(consumer, winner, loser, ws, ls)
    else:
        await save_match_history(consumer, winner, loser, ws, ls)

    winner_profile = await get_profile_data(consumer, winner)
    loser_profile = await get_profile_data(consumer, loser)

    match_round = 0
    if consumer.isTournament:
        match_round = await get_round(consumer)

    data = {"type": "end_game", "match_id": consumer.match_id, "winner": wn,
        "loser": ln, "score": f'{ws}-{ls}',
        "winner_profile": winner_profile,
        "loser_profile": loser_profile,
        "player1_score": consumer.score1,
        "player2_score": consumer.score2,
        "match_round": match_round
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
def get_profile_data(consumer, player):
    # print_yellow(f'player:    {player}')
    serializer = ProfileSerializer(player)
    return serializer.data

@database_sync_to_async
def get_round(consumer):
    match = TournamentMatch.objects.get(id=consumer.match_id)
    return match.round_number

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

@database_sync_to_async
def save_tounament_match(consumer, winner, loser, winner_score, loser_score):
    pass
