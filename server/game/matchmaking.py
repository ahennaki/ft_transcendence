from channels.db                import database_sync_to_async
from .models                    import PlayerQueue, Match
from prfl.models                import Profile
from prfl.serializers           import ProfileSerializer
from asyncio                    import Lock
from authentication.utils       import print_red, print_green, print_yellow
import asyncio

matchmaking_lock = Lock()

@database_sync_to_async
def find_match(consumer):
    queue = PlayerQueue.objects.order_by('joined_at')

    if queue.count() >= 2:
        player1 = queue[0].player
        player2 = queue[1].player

        match = Match.objects.create(player1=player1, player2=player2, status='ongoing')
        PlayerQueue.objects.filter(player__in=[player1, player2]).delete()

        print_yellow(f'player {player1.username} matched with {player2.username}')
        return match, player1, player2
    return None, None, None

async def matchmaking(consumer):
    async with matchmaking_lock:
        match, player1, player2 = await find_match(consumer)
        if isinstance(match, Match):
            await notify_players(consumer, player1, player2, match)
        else:
            data = {'type': 'waiting', 'message': 'Waiting for another player...'}
            await consumer.channel_layer.group_send(
            f'user_{consumer.user.username}',
            {'type': 'waiting', 'data': data})

async def notify_players(consumer, player1, player2, match):
    player1_data = await get_profile_data(consumer, player1)
    player2_data = await get_profile_data(consumer, player2)
    player_username1, player_username2 = await get_player_usernames(consumer, match.id)
    
    await consumer.channel_layer.group_send(
        f"user_{player_username1}",
        {'type': 'send_match_info', 'player': player2_data,
            'match_id': match.id, 'player_number': 1}
    )
    await consumer.channel_layer.group_send(
        f"user_{player_username2}",
        {'type': 'send_match_info', 'player': player1_data,
            'match_id': match.id, 'player_number': 2}
    )

@database_sync_to_async
def get_profile_data(consumer, player):
    serializer = ProfileSerializer(player)
    return serializer.data

@database_sync_to_async
def get_player_usernames(consumer, match_id):
    try:
        match = Match.objects.get(id=match_id)
        return match.player1.user.username, match.player2.user.username
    except Match.DoesNotExist:
        return None, None

@database_sync_to_async
def get_player_profile(consumer, invited_id):
    try:
        profile = Profile.objects.get(id=invited_id)
        return profile
    except Profile.DoesNotExist:
        return None
