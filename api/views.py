from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import UserSerializer, MovieSerializer,RecentSearchSerializer, FavoriteMovieSerializer, TopRatedTVShowSerializer, TVShowCustomizationSerializer, CustomizedTopRatedTVShowSerializer, FavoriteActorSerializer, ActorMovieSerializer
from .services import get_tokens_for_user, search_movies_by_title, search_tv_shows_by_title, add_favorite_movie, get_top_rated_tv_shows, add_favorite_actor, remove_favorite_actor, get_movie_details_and_watch_providers
from .serializers import RecentSearchSerializer, MovieFeedbackSerializer, TVShowPreferenceSerializer, MovieRecommendationFeedbackSerializer, TVShowRecommendationSerializer, TopRatedMovieSerializer, MovieCastAndCrewSerializer, ActorSerializer, MovieWatchlistSerializer
from .models import RecentTVShowSearch, TVShowPreference, MovieRecommendationFeedback, FavoriteMovie
from .services import get_trending_movies, submit_movie_feedback, get_trending_tv_shows, get_movie_title, get_movie_recommendations, save_feedback, get_top_rated_movies, get_movie_details_and_cast, add_movie_to_watchlist
from .services import TV_GENRES, get_tv_show_recommendations, fetch_tv_show_title, save_tv_show_recommendation, remove_tv_show_recommendation, get_customized_top_rated_tv_shows, TV_SHOW_GENRES, get_actor_movies

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
    
class MovieRecommendationsView(APIView):
    def get(self, request, movie_id):
        """Retrieve recommended movies for a given movie ID."""
        movie_title = get_movie_title(movie_id)
        
        if movie_title is None:
            return Response({"error": "Movie not found."}, status=status.HTTP_404_NOT_FOUND)

        recommendations = get_movie_recommendations(movie_id)

        if recommendations is None:
            return Response({"movie": movie_title, "recommendations": []}, status=status.HTTP_200_OK)

        return Response({"movie": movie_title, "recommendations": recommendations}, status=status.HTTP_200_OK)
    
class MovieRecommendationFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        """Allows users to like or dislike a recommended movie."""
        user = request.user
        recommended_movie_id = request.data.get("recommended_movie_id")
        feedback = request.data.get("feedback", "").lower()  # Convert feedback to lowercase

        valid_feedback = ["like", "dislike"]

        if not recommended_movie_id or feedback not in valid_feedback:
            return Response(
                {"error": "Invalid input. Provide 'recommended_movie_id' and feedback ('like' or 'dislike')."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the feedback already exists
        existing_feedback = MovieRecommendationFeedback.objects.filter(
            user=user, movie_id=movie_id, recommended_movie_id=recommended_movie_id
        ).first()

        if existing_feedback:
            return Response(
                {"error": "You have already provided feedback for this recommendation."},
                status=status.HTTP_409_CONFLICT
            )

        # Save feedback
        feedback_instance = save_feedback(user, movie_id, recommended_movie_id, feedback)
        serializer = MovieRecommendationFeedbackSerializer(feedback_instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TVShowRecommendationsView(APIView):
    """Returns recommended TV shows based on a given TV show ID."""

    def get(self, request, tv_show_id):
        """Fetch and return recommended TV shows."""
        recommendations = get_tv_show_recommendations(tv_show_id)
        
        if "error" in recommendations:
            return Response(recommendations, status=status.HTTP_400_BAD_REQUEST)

        # Optional: Fetch the TV show title for better response clarity
        tv_show_title = fetch_tv_show_title(tv_show_id)

        return Response(
            {
                "TV Show Recommendations for": tv_show_title,
                "recommendations": recommendations
            },
            status=status.HTTP_200_OK
        )

class SaveTVShowRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, tvShowId):
        """Save a specific TV show recommendation."""
        user = request.user
        recommended_tv_show_id = request.data.get("recommended_tv_show_id")

        if not recommended_tv_show_id:
            return Response({"error": "recommended_tv_show_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        recommendation, created = save_tv_show_recommendation(user, tvShowId, recommended_tv_show_id)
        serializer = TVShowRecommendationSerializer(recommendation)

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message": "Recommendation already exists.", "data": serializer.data}, status=status.HTTP_200_OK)
    
class RemoveTVShowRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, tvShowId):
        """
        Remove a specific TV show recommendation.
        """
        recommended_tv_show_id = request.data.get("recommended_tv_show_id")

        if not recommended_tv_show_id:
            return Response({"error": "recommended_tv_show_id is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        result = remove_tv_show_recommendation(request.user, tvShowId, recommended_tv_show_id)

        if "error" in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)

class TopRatedMoviesView(APIView):
    def get(self, request):
        """Retrieve the top-rated movies from TMDb."""
        movies = get_top_rated_movies()

        if "error" in movies:
            return Response(movies, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = TopRatedMovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddFavoriteMovieView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add a top-rated movie to the user's favorites."""
        user = request.user
        movie_id = request.data.get("movie_id")
        movie_title = request.data.get("movie_title")

        if not movie_id or not movie_title:
            return Response({"error": "movie_id and movie_title are required."}, status=status.HTTP_400_BAD_REQUEST)

        result = add_favorite_movie(user, movie_id, movie_title)
        return Response(result, status=status.HTTP_201_CREATED)

class TopRatedTVShowsView(APIView):
    def get(self, request):
        """Retrieve top-rated TV shows from TMDb API."""
        tv_shows = get_top_rated_tv_shows()
        
        if "error" in tv_shows:
            return Response(tv_shows, status=status.HTTP_400_BAD_REQUEST)

        serializer = TopRatedTVShowSerializer(tv_shows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomizeTopRatedTVShowsView(APIView):
    def post(self, request):
        """Customize how top-rated TV shows are displayed based on user preferences."""
        serializer = TVShowCustomizationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        preferences = serializer.validated_data
        tv_shows = get_customized_top_rated_tv_shows(
            preferred_genres=preferences.get("preferred_genres"),
            min_rating=preferences.get("min_rating"),
            release_year=preferences.get("release_year")
        )

        if "error" in tv_shows:
            return Response(tv_shows, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            "filtered_tv_shows": CustomizedTopRatedTVShowSerializer(tv_shows, many=True).data,
            "available_genres": TV_SHOW_GENRES
        }
        return Response(response_data, status=status.HTTP_200_OK)

class MovieCastView(APIView):
    """Retrieve the movie title, cast, and crew for a specific movie."""

    def get(self, request, movie_id):
        movie_data = get_movie_details_and_cast(movie_id)

        if "error" in movie_data:
            return Response({"error": movie_data["error"]}, status=status.HTTP_404_NOT_FOUND)

        serializer = MovieCastAndCrewSerializer(movie_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddFavoriteActorView(APIView):
    """Add a cast member to the user's favorite actors list."""
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_id):
        actor_id = request.data.get("actor_id")
        actor_name = request.data.get("actor_name")
        profile_path = request.data.get("profile_path")  # Optional

        if not actor_id or not actor_name:
            return Response({"error": "actor_id and actor_name are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        favorite, created = add_favorite_actor(request.user, actor_id, actor_name, profile_path)
        serializer = FavoriteActorSerializer(favorite)

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message": "Actor already in favorites.", "data": serializer.data}, status=status.HTTP_200_OK)
    
class ActorMoviesView(APIView):
    """Retrieve movies an actor has starred in"""

    def get(self, request, personId):
        """Fetch movies featuring a specific actor"""
        data = get_actor_movies(personId)

        if data is None:
            return Response({"error": "Failed to fetch actor's movies."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serialized_data = ActorSerializer(data).data

        return Response(serialized_data, status=status.HTTP_200_OK)
    
class RemoveFavoriteActorView(APIView):
    """Remove an actor from the user's favorite list."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, personId):
        """Handles deleting a favorite actor."""
        user = request.user

        success = remove_favorite_actor(user, personId)
        if success:
            return Response({"message": "Actor removed from favorites."}, status=status.HTTP_200_OK)
        return Response({"error": "Actor not found in favorites."}, status=status.HTTP_404_NOT_FOUND)
    
class MovieWatchProvidersView(APIView):
    """Retrieve streaming services and movie title."""

    def get(self, request, movieId):
        """Fetches movie title and streaming services for a given movie."""
        movie_title, providers_data = get_movie_details_and_watch_providers(movieId)

        if not movie_title:
            return Response({"error": "Movie not found."}, status=status.HTTP_404_NOT_FOUND)

        if not providers_data:
            return Response({"movie_id": movieId, "movie_title": movie_title, "watch_providers": {}}, status=status.HTTP_200_OK)

        return Response({"movie_id": movieId, "movie_title": movie_title, "watch_providers": providers_data}, status=status.HTTP_200_OK)
    
class AddMovieToWatchlistView(APIView):
    """API to add a movie to the user's watchlist."""
    permission_classes = [IsAuthenticated]  # Requires user authentication

    def post(self, request):
        """Handles adding a movie to the watchlist."""
        movie_id = request.data.get("movie_id")
        movie_title = request.data.get("movie_title")
        poster_path = request.data.get("poster_path")  # Optional

        if not movie_id or not movie_title:
            return Response({"error": "movie_id and movie_title are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        watchlist_item, created = add_movie_to_watchlist(request.user, movie_id, movie_title, poster_path)
        serializer = MovieWatchlistSerializer(watchlist_item)

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message": "Movie already in watchlist.", "data": serializer.data}, status=status.HTTP_200_OK)