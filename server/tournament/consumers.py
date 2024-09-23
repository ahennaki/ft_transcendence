import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db                import database_sync_to_async
from .models                    import Tournament, TournamentParticipant, Match
from .serializers               import *
from django.db                  import transaction
from prfl.models                import Profile
from game.consumers             import active_connections
from rest_framework             import serializers

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
        profile_exists = await self.check_user_profile()
        self.isGaming = False

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

    async def disconnect(self, close_code):
        if self.user.id in active_connections:
            active_connections[self.user.id] -= 1
            if active_connections[self.user.id] == 0:
                del active_connections[self.user.id]
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "create_tournament":
                await self.handle_create_tournament(data)
            elif action == "join_tournament":
                await self.handle_join_tournament(data)
            else:
                await self.send_json({"error": "Invalid action."})
        except json.JSONDecodeError:
            await self.send_json({"error": "Invalid JSON."})
        except Exception as e:
            await self.send_json({"error": "An unexpected error occurredduring receive."})

    async def handle_create_tournament(self, data):
        tournament_name = data.get("tournament_name")
        alias = data.get("alias")

        if not tournament_name or not alias:
            await self.send_json({"error": "tournament_name and alias are required."})
            return

        serializer = TournamentCreateSerializer(data={
            "tournament_name": tournament_name,
            "alias": alias
        }, context={"user": self.user})  # Use self.user

        try:
            is_valid = await validate_serializer(serializer)
            if is_valid:
                tournament = await save_serializer(serializer)
                group_name = f"tournament_{tournament.id}"
                await self.channel_layer.group_add(
                    group_name,
                    self.channel_name
                )
                participants = await get_participants(tournament)
                participant_serializer = TournamentParticipantSerializer(participants, many=True)
                await self.send_json({
                    "type": "tournament_created",
                    "message": "Tournament created successfully.",
                    "tournament": {
                        "id": str(tournament.id),
                        "name": tournament.name,
                        "status": tournament.status,
                        "participants": participant_serializer.data
                    }
                })
            else:
                await self.send_json({"error": serializer.errors})
        except serializers.ValidationError as ve:
            await self.send_json({"error": ve.detail})
        except Exception as e:
            await self.send_json({"error": "An error occurred while creating the tournament."})

    async def handle_join_tournament(self, data):
        tournament_name = data.get("tournament_name")
        alias = data.get("alias")

        if not tournament_name or not alias:
            await self.send_json({"error": "tournament_name and alias are required."})
            return

        serializer = TournamentJoinSerializer(data={
            "tournament_name": tournament_name,
            "alias": alias
        }, context={"user": self.user})  # Use self.user

        try:
            is_valid = await validate_serializer(serializer)
            if is_valid:
                participant = await save_serializer(serializer)
                tournament = participant.tournament
                group_name = f"tournament_{tournament.id}"
                await self.channel_layer.group_add(
                    group_name,
                    self.channel_name
                )
                participants = await get_participants(tournament)
                participant_serializer = TournamentParticipantSerializer(participants, many=True)
                await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": "participants_update",
                        "participants": participant_serializer.data
                    }
                )
                await self.send_json({
                    "type": "join_tournament",
                    "message": "Successfully joined the tournament.",
                    "participants": participant_serializer.data
                })
            else:
                await self.send_json({"error": serializer.errors})
        except serializers.ValidationError as ve:
            await self.send_json({"error": ve.detail})
        except Exception as e:
            await self.send_json({"error": "An error occurred while joining the tournament."})

    async def participants_update(self, event):
        participants = event.get("participants")
        await self.send_json({
            "type": "participants_update",
            "participants": participants
        })

    async def send_json(self, content, **kwargs):
        await self.send(text_data=json.dumps(content), **kwargs)

    @database_sync_to_async
    def check_user_profile(self):
        try:
            return self.user.profile is not None
        except Profile.DoesNotExist:
            return False
