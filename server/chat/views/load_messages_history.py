from rest_framework             import generics, status
from django.http                import JsonResponse
from authentication.utils       import Authenticate
from ..models                   import Chat, Message

class LoadMessagesView(generics.GenericAPIView):
    pass
    # def post(self, request):
    #     user = Authenticate(request)
    #     if not user.is_authenticated:
    #         return JsonResponse(
    #             {"message": "User is not authenticated"},
    #             status = status.HTTP_401_UNAUTHORIZED
    #         )
    #     username = request.data.get('username')
    #     start = request.data.get('start')
    #     if not username or not start:
    #         return JsonResponse(
    #             {"message": "Username is required"},
    #             status = status.HTTP_400_BAD_REQUEST
    #         )
    #     try:
    #         profile = Profile.objects.get(username=username)
    #     except Profile.DoesNotExist:
    #         return JsonResponse(
    #             {"message": "User not found"},
    #             status = status.HTTP_404_NOT_FOUND
    #         )
    #     room_name = f"{user.profile.id}-{profile.id}" if user.profile.id >= profile.id else f"{profile.id}-{user.profile.id}"
    #     try:
    #         chat = Chat.objects.get(name=room_name)
    #     except Chat.DoesNotExit:
    #         return JsonResponse {
    #             "message": "Chat not found",
    #             "status": status.HTTP_404_NOT_FOUND
    #         }
    #     messages = Message.objects.filter(
    #         Q(chat=chat, receiver=user.profile) | Q(chat=chat, sender=user.profile)
    #     ).order_by('-created_at')[start:30]
    #     return JsonResponse({
    #         "messages": [{
    #             'id': message.id,
    #             'sender_id': message.sender_id,
    #             'receiver_id': message.receiver_id,
    #             'content': message.content,
    #             'created_at': message.created_at.isoformat(),
    #             'is_read': message.is_read
    #         } for message in messages]
    #         },
    #         status=status.HTTP_200_OK
    #     )
