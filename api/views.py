from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import UserSerializer, MovieSerializer,RecentSearchSerializer
from .services import get_tokens_for_user, search_movies_by_title, search_tv_shows_by_title 
from .serializers import RecentSearchSerializer, MovieFeedbackSerializer, TVShowPreferenceSerializer
from .models import RecentTVShowSearch, TVShowPreference
from .services import get_trending_movies, submit_movie_feedback, get_trending_tv_shows
from .services import TV_GENRES

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

class TVShowSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("query", "").strip()
        if not query:
            return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        tv_shows = search_tv_shows_by_title(query)
        return Response(tv_shows, status=status.HTTP_200_OK)

class ClearRecentTVShowSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        deleted_count, _ = RecentTVShowSearch.objects.filter(user=user).delete()

        if deleted_count > 0:
            return Response({"message": "Recent TV show searches cleared successfully."}, status=status.HTTP_200_OK)
        return Response({"message": "No recent TV show searches to clear."}, status=status.HTTP_200_OK)

class TrendingMoviesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        trending_movies = get_trending_movies()
        return Response(trending_movies, status=status.HTTP_200_OK)
    
class SubmitMovieFeedbackView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users only

    def post(self, request):
        serializer = MovieFeedbackSerializer(data=request.data)

        if serializer.is_valid():
            movie_title = serializer.validated_data['movie_title']
            rating = serializer.validated_data['rating']
            comment = serializer.validated_data.get('comment', None)
            user = request.user  # Get the authenticated user

            # Call service to save feedback
            feedback = submit_movie_feedback(movie_title, rating, comment, user)

            if feedback:
                rating_text = "Like" if rating == "1" else "Dislike"
                return Response(
                    {
                        "message": f"Feedback submitted successfully! You {rating_text} the movie '{movie_title}'.",
                        "user": user.username,
                        "movie_title": movie_title,
                        "rating": rating_text,
                        "comment": comment or "No comment",
                        "created_at": feedback.created_at  # Return created_at instead of timestamp
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response({"error": "Error saving feedback."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class TrendingTVShowsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        trending_tv_shows = get_trending_tv_shows()
        return Response(trending_tv_shows, status=status.HTTP_200_OK)
    
class TVShowPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the user's current TV show preferences along with available genres."""
        preference, created = TVShowPreference.objects.get_or_create(user=request.user)
        genres_with_ids = {genre: TV_GENRES[genre] for genre in preference.preferred_genres}

        return Response({
            "preferred_genres": preference.preferred_genres,
            "genre_ids": genres_with_ids,
            "available_genres": TV_GENRES  # Include all available genres
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Update the user's TV show preferences."""
        preference, created = TVShowPreference.objects.get_or_create(user=request.user)
        
        # Case-insensitive genre lookup
        available_genres_lower = {genre.lower(): genre_id for genre, genre_id in TV_GENRES.items()}
        
        user_input_genres = request.data.get("preferred_genres", [])

        valid_genres = []
        invalid_genres = []

        for genre in user_input_genres:
            lower_genre = genre.lower()
            if lower_genre in available_genres_lower:
                # Add the correctly formatted genre name
                valid_genres.append(next(k for k, v in TV_GENRES.items() if v == available_genres_lower[lower_genre]))
            else:
                invalid_genres.append(genre)

        # Save valid genres
        preference.preferred_genres = valid_genres
        preference.save()

        # Construct the response
        response_data = {
            "preferred_genres": valid_genres,
            "genre_ids": {genre: TV_GENRES[genre] for genre in valid_genres}
        }

        # Add error message if there are invalid genres
        if invalid_genres:
            response_data["error"] = {
                "preferred_genres": [
                    f"Invalid genres: {', '.join(invalid_genres)}. Use valid genre names."
                ]
            }

        # Add available genres at the bottom
        response_data["available_genres"] = TV_GENRES
        
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST if invalid_genres else status.HTTP_200_OK)
