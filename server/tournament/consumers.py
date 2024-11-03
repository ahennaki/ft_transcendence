import json
import time
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db                import database_sync_to_async
from .models                    import Tournament, TournamentParticipant, TournamentMatch
from .serializers               import *
from django.db                  import transaction
from prfl.models                import Profile
from game.consumers             import active_connections
from rest_framework             import serializers
from authentication.utils       import print_red, print_green, print_yellow
from game.game_loop             import game_loop, send_score_update
from .match_end                 import end_match
from game.paddle                import update_paddle, move_paddle
from game.helpers               import initialize_data, score_update, reinitialize_data

@database_sync_to_async
def validate_serializer(serializer):
    return serializer.is_valid()

@database_sync_to_async
def save_serializer(serializer):
    return serializer.save()

@database_sync_to_async
def get_participants(tournament):
    return list(tournament.participants.select_related('user__user').all())

class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print_green(f'{self.user.username} is connected')
        profile_exists = await self.check_user_profile()

        if not self.user.is_authenticated or not profile_exists:
            await self.close()
            return

        if self.user.id not in active_connections:
            active_connections[self.user.id] = 0
        active_connections[self.user.id] += 1

        await self.accept()

        if active_connections[self.user.id] > 1:
            data = {'type': 'already_connected', 'message': 'User already connected from another tab'}
            await self.send(text_data=json.dumps({'type': 'already_connected', 'data': data}))
            await self.close()
            return

        self.group_name = f"user_{self.user.username}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await initialize_data(self)
        self.isTournament = True

    async def disconnect(self, close_code):
        print_red(f'{self.user.username} is disconnected')
        if self.user.id in active_connections:
            active_connections[self.user.id] -= 1
            # print_yellow(f'active_connection: {active_connections[self.user.id]}')
            if active_connections[self.user.id] == 0:
                del active_connections[self.user.id]
        if hasattr(self, 'group_name'):
            if not (await self.handle_disconnect()):
                await end_match(self, True)
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            tournament = await self.get_tounament()
            await self.disconnect_participant(tournament)
            if tournament and tournament.status == 'upcoming':
                await self.remove_participant(tournament)
                participants = await get_participants(tournament)
                participant_serializer = TournamentParticipantSerializer(participants, many=True)
                await self.channel_layer.group_send(f"tournament_{tournament.id}",
                    {"type": "participants_update", "participants": participant_serializer.data})
            elif tournament and tournament.status == 'ongoing':
                pass #todo
            self.isGaming = False
            self.isTournament = False

    @database_sync_to_async
    def handle_disconnect(self):
        match = TournamentMatch.objects.get(id=self.match_id)
        if self.isGaming:
            return 0
        elif not self.isGaming and self.match_id:
            print_red(f'{self.user.username} is disconnected and send end_match')
            match.number_player -= 1
            match.save()
            if match.number_player == 1:
                return 0
            else:
                match.interupted = True #todo
                match.save()
        return 1

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "create_tournament":
            print_green(f'data: {data}')
            await self.create_tournament(data)
        elif action == "join_tournament":
            await self.join_tournament(data)
        elif action == "start_game":
            await self.start_game(data)
        elif action == "match_received":
            print_yellow(f'data: {data}')
            self.match_id = data['match_id']
            self.match, self.player1_username, self.player2_username = await self.get_player_usernames()
        elif action == 'move_paddle':
            await move_paddle(self, data)
        elif action == 'update_paddle':
            await update_paddle(self, data)
        elif action == 'score_update':
            await score_update(self, data)
        elif action == 'stop_game':
            if self.isGaming:
                self.isGaming = False
        elif action == 'disconnect':
            initialize_data(self)
            await self.close()
        else:
            await self.send_json({"error": "Invalid action."})

    async def start_game(self, data):
        print_green(f'{self.user.username} start the game!')
        self.start_time = time.time()
        self.isGaming = True
        self.isTournament = True
        self.match_id = data['match_id']
        self.match, self.player1_username, self.player2_username = await self.get_player_usernames()
        await reinitialize_data(self)
        await send_score_update(self)
        if not (await self.check_connection()):
            await end_match(self, True)
        if self.user.username == self.player1_username:
            asyncio.create_task(game_loop(self))

    async def create_tournament(self, data):
        tournament_name = data.get("tournament_name")
        alias = data.get("alias")

        if not tournament_name or not alias:
            await self.send_json({"error": "tournament_name and alias are required."})
            return

        serializer = TournamentCreateSerializer(data={
            "tournament_name": tournament_name, "alias": alias
        }, context={"user": self.user})

        try:
            is_valid = await validate_serializer(serializer)
            if is_valid:
                tournament = await save_serializer(serializer)
                self.tournament_id = tournament.id
                group_name = f"tournament_{tournament.id}"
                await self.channel_layer.group_add(group_name, self.channel_name)
                participants = await get_participants(tournament)
                participant_serializer = TournamentParticipantSerializer(participants, many=True)
                await self.send_json({"type": "tournament_created", "message": "Tournament created successfully.",
                    "tournament": {"id": str(tournament.id), "name": tournament.name,
                        "status": tournament.status, "participants": participant_serializer.data}})
            else:
                await self.send_json({"error": serializer.errors})
        except serializers.ValidationError as ve:
            await self.send_json({"error": ve.detail})

    async def join_tournament(self, data):
        print_yellow(f'dsta: {data}')
        tournament_name = data.get("tournament_name")
        alias = data.get("alias")

        if not tournament_name or not alias:
            await self.send_json({"error": "tournament_name and alias are required."})
            return

        serializer = TournamentJoinSerializer(data={
            "tournament_name": tournament_name, "alias": alias
        }, context={"user": self.user})

        try:
            is_valid = await validate_serializer(serializer)
            if is_valid:
                participant = await save_serializer(serializer)
                tournament = participant.tournament
                self.tournament_id = tournament.id
                group_name = f"tournament_{tournament.id}"
                await self.channel_layer.group_add(group_name, self.channel_name)
                participants = await get_participants(tournament)
                participant_serializer = TournamentParticipantSerializer(participants, many=True)
                await self.channel_layer.group_send(
                    group_name,
                    {"type": "participants_update", "participants": participant_serializer.data})
                await self.send_json({"type": "join_tournament", "message": "Successfully joined.",
                    "participants": participant_serializer.data})
            else:
                await self.send_json({"error": serializer.errors})
        except serializers.ValidationError as ve:
            await self.send_json({"error": ve.detail})

    async def participants_update(self, event):
        participants = event.get("participants")
        await self.send_json({"type": "participants_update", "participants": participants})

    async def send_json(self, content, **kwargs):
        await self.send(text_data=json.dumps(content), **kwargs)

    async def update_winner(self, event):
        winners = event.get("winners")
        round_tour = event.get("round")
        await self.send_json({"type": "update_winner", "winners": winners, "round": round_tour})

    async def send_match_info(self, event):
        match_data = event.get("match_data")
        self.player_number = event['player_number']
        await self.send_json({"type": "match_detail", "match": match_data,
        'player_number': self.player_number})

    async def game_update(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    async def paddle_update(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    async def score_update(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    async def end_game(self, event):
        data = event.get('data', {})
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def get_player_usernames(self):
        try:
            match = TournamentMatch.objects.get(id=self.match_id)
            return match, match.player1.user.username, match.player2.user.username
        except TournamentMatch.DoesNotExist:
            return None, None, None

    @database_sync_to_async
    def check_connection(self):
        match = TournamentMatch.objects.get(id=self.match_id)
        if match.player1.isDisconnect:
            self.score2 = 10
            return 0
        elif match.player2.isDisconnect:
            self.score1 = 10
            return 0
        return 1

    @database_sync_to_async
    def get_match(self, match_id):
        try:
            match = TournamentMatch.objects.get(id=match_id)
            return match
        except TournamentMatch.DoesNotExist:
            return None

    @database_sync_to_async
    def check_user_profile(self):
        try:
            return self.user.profile is not None
        except Profile.DoesNotExist:
            return False

    @database_sync_to_async
    def get_tounament(self):
        profile = Profile.objects.get(user=self.user)
        return Tournament.objects.filter(participants__user=profile, status='upcoming').first()

    @database_sync_to_async
    def remove_participant(self, tournament):
        profile = Profile.objects.get(user=self.user)
        TournamentParticipant.objects.filter(tournament=tournament, user=profile).delete()

    @database_sync_to_async
    def disconnect_participant(self, tournament):
        try:
            participant = TournamentParticipant.objects.get(tournament=tournament, user=self.user.profile)
            participant.isDisconnect = True
            participant.save()
        except TournamentParticipant.DoesNotExist:
            print(f"Participant not found for user {self.user.username} in tournament {tournament}")
