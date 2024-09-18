from channels.db                import database_sync_to_async
from .models                    import MatchHistory, Match
from prfl.models                import Profile
from authentication.utils       import print_red, print_green, print_yellow

async def end_game(consumer, isDisconnect):
    wn, ln, winner, loser, ws, ls = determine_winner_loser(consumer, isDisconnect)

    print_green('end of the game!')
    await save_match_history(
        consumer, winner, loser, ws, ls
    )
    data = {"type": "end_game", "winner": wn,
        "loser": ln, "score": f'{ws}-{ls}'
    }

    await consumer.channel_layer.group_send(
        f"user_{consumer.player1_id}",
        {"type": "end_game", "data": data}
    )
    await consumer.channel_layer.group_send(
        f"user_{consumer.player2_id}",
        {"type": "end_game", "data": data}
    )

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
        if consumer.user.id == consumer.player2_id:
            consumer.score1 = 10
            return 1, 2, consumer.match.player1, consumer.match.player2, consumer.score1, consumer.score2
        elif consumer.user.id == consumer.player1_id:
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
