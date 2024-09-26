from rest_framework 			import generics, status
from django.http                import JsonResponse
from .models 					import Tournament, TournamentParticipant, TournamentMatch
from .helpers					import progress_tournament
from authentication.utils       import print_red, print_green, print_yellow
from .serializers 				import (
    TournamentNameSerializer,
    TournamentSerializer,
    AliasCheckSerializer,
    TournamentCreateSerializer,
    TournamentJoinSerializer,
    MatchUpdateSerializer,
    TournamentNameCheckSerializer
)

class TournamentNameListView(generics.GenericAPIView):
    queryset = Tournament.objects.filter(status='upcoming')
    serializer_class = TournamentNameSerializer

    def get(self, request, *args, **kwargs):
        tournaments = self.get_queryset()
        serializer = self.get_serializer(tournaments, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

class AliasAvailabilityCheckView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        serializer = AliasCheckSerializer(data=request.data)
        print_yellow(f'data= {request.data}')
        
        if serializer.is_valid():
            alias_taken = serializer.validated_data['alias_taken']
            if not alias_taken:
                return JsonResponse({'success': 'valide name'}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'error': 'invalide name'}, status=status.HTTP_400_BAD_REQUEST)
        print_red(f'errors= {serializer.errors}')
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TournamentNameCheckView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        serializer = TournamentNameCheckSerializer(data=request.data)
        if serializer.is_valid():
            name_taken = serializer.validated_data['name_taken']
            print_red(f'name_taken {name_taken}')
            if not name_taken:
                return JsonResponse({'success': 'valide name'}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'error': 'invalide name'}, status=status.HTTP_400_BAD_REQUEST)

class CreateTournamentView(generics.CreateAPIView):
    serializer_class = TournamentCreateSerializer

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

    def get_queryset(self):
        return Tournament.objects.filter(status='upcoming')

class UpdateMatchView(generics.UpdateAPIView):
    queryset = TournamentMatch.objects.all()
    serializer_class = MatchUpdateSerializer

    def update(self, request, *args, **kwargs):
        match = self.get_object()
        serializer = self.get_serializer(match, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            progress_tournament(match.tournament)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
