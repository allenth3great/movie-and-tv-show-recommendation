from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # Fixed import
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import UserSerializer, MovieSerializer,RecentSearchSerializer
from .services import get_tokens_for_user, search_movies_by_title  
from .serializers import RecentSearchSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            tokens = get_tokens_for_user(user)
            return Response(tokens, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class MovieSearchView(APIView):
    permission_classes = [IsAuthenticated]  # Fixed

    def get(self, request):
        query = request.query_params.get('query', "").strip()
        if not query:
            return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        movie_data = search_movies_by_title(query)
        return Response(movie_data, status=status.HTTP_200_OK)
    
class SaveRecentSearchView(generics.CreateAPIView):
    serializer_class = RecentSearchSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can save recent searches

    def perform_create(self, serializer):
        # Automatically associate the current user with the recent search
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        movie_title = request.data.get('movie_title')
        
        if not movie_title:
            return Response({"error": "Movie title is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform the save operation
        return super().create(request, *args, **kwargs)
