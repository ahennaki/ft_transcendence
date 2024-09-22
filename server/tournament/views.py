from rest_framework 			import generics, status
from rest_framework.permissions import IsAuthenticated
from django.http                import JsonResponse
from .serializers 				import TournamentSerializer, TournamentCreateSerializer, TournamentJoinSerializer
from .models 					import Tournament, TournamentParticipant, Match
from .utils						import progress_tournament

class CreateTournamentView(generics.CreateAPIView):
    serializer_class = TournamentCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            tournament = serializer.save()
            response_serializer = TournamentSerializer(tournament)
            return JsonResponse(response_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JoinTournamentView(generics.CreateAPIView):
    serializer_class = TournamentJoinSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            participant = serializer.save()
            return JsonResponse({"detail": "Successfully joined the tournament."}, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListTournamentsView(generics.ListAPIView):
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Tournament.objects.filter(status='upcoming')

class UpdateMatchView(generics.UpdateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchUpdateSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        match = self.get_object()
        serializer = self.get_serializer(match, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            progress_tournament(match.tournament)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
