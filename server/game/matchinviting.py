from channels.db                import database_sync_to_async
from .models                    import Match, InviteQueue
from prfl.models                import Profile
from prfl.serializers           import ProfileSerializer
from asyncio                    import Lock
from authentication.utils       import print_red, print_green, print_yellow
import asyncio

matchinviting_lock = Lock()

@database_sync_to_async
def check_match_ids(consumer, queue):
    i = 0
    while i < queue.count():
        requests = get_player_requests(queue[i].invited_id)
        if consumer.user.profile.id in requests:
            return queue[i].player
        i += 1
    return None

@database_sync_to_async
def find_match(consumer):
    queue = InviteQueue.objects.order_by('joined_at')

    if queue.count() >= 1:
        player1 = consumer.user.profile
        player2 = check_match_ids(consumer, queue)

        if player2:
            match = Match.objects.create(player1=player1, player2=player2, status='ongoing')
            InviteQueue.objects.filter(player=player2).delete()

            print_yellow(f'invite_player {player1.username} matched with {player2.username}')
            return match, player1, player2

    add_inviter_to_queue(consumer)
    return None, None, None


async def invited_player(consumer):
    async with matchinviting_lock:
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
def get_player_requests(invited_id):
    try:
        profile = Profile.objects.get(id=invited_id)
        return profile.play_requests
    except Profile.DoesNotExist:
        return None

@database_sync_to_async
def add_inviter_to_queue(consumer):
    profile = consumer.user.profile
    InviteQueue.objects.get_or_create(player=profile, invite_id=consumer.user.profile.id)
