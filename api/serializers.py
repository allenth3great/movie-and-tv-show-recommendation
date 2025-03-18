from django.contrib.auth.models import User
from rest_framework import serializers
from .models import RecentSearch, MovieFeedback, TVShowPreference, MovieRecommendationFeedback, TVShowRecommendation, FavoriteMovie, FavoriteActor
from django.utils.timezone import localtime
from .services import TV_GENRES, fetch_movie_title

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class MovieSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    overview = serializers.CharField()
    release_date = serializers.CharField()
    poster_path = serializers.CharField(allow_null=True)

    def get_poster_url(self, obj):
        return f"https://image.tmdb.org/t/p/w500{obj['poster_path']}" if obj.get('poster_path') else None
    
class RecentSearchSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    searched_at = serializers.SerializerMethodField()

    def get_searched_at(self, obj):
       return localtime(obj.searched_at).isoformat()
    
    def get_user(self, obj):
        # Assuming 'user' is a ForeignKey to the User model
        return obj.user.username  # Fetches the actual username

    class Meta:
        model = RecentSearch
        fields = ['id', 'user', 'movie_title', 'searched_at']
        read_only_fields = ['id', 'searched_at']
    
class MovieFeedbackSerializer(serializers.ModelSerializer):
    rating = serializers.CharField()  # Handle rating as a CharField
    timestamp = serializers.DateTimeField(read_only=True)  # Include timestamp in the response

    class Meta:
        model = MovieFeedback
        fields = ['movie_title', 'rating', 'comment', 'timestamp']

    def validate_rating(self, value):
        value = str(value).strip()
        if value not in ["0", "1"]:
            raise serializers.ValidationError(
                "Invalid rating. Valid choices are '0' (Dislike) or '1' (Like). Please provide one of these values."
            )
        return value
    
class TVShowPreferenceSerializer(serializers.ModelSerializer):
    preferred_genres = serializers.ListField(
        child=serializers.CharField(),  # Expecting genre names as input
        required=False
    )

    def validate_preferred_genres(self, value):
        """Validate genre names and convert them to IDs."""
        invalid_genres = [genre for genre in value if genre not in TV_GENRES]
        if invalid_genres:
            raise serializers.ValidationError(
                f"Invalid genres: {', '.join(invalid_genres)}. Use valid genre names."
            )
        return value  # Store genre names

    class Meta:
        model = TVShowPreference
        fields = ['preferred_genres']

class MovieRecommendationFeedbackSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)  # Show username instead of user ID
    movie_title = serializers.SerializerMethodField()
    recommended_movie_title = serializers.SerializerMethodField()

    class Meta:
        model = MovieRecommendationFeedback
        fields = [
            "id", "username", "movie_id", "movie_title",
            "recommended_movie_id", "recommended_movie_title",
            "feedback", "created_at"
        ]
        read_only_fields = ["id", "username", "created_at", "movie_title", "recommended_movie_title"]

    def get_movie_title(self, obj):
        return fetch_movie_title(obj.movie_id) or "Unknown Movie"

    def get_recommended_movie_title(self, obj):
        return fetch_movie_title(obj.recommended_movie_id) or "Unknown Movie"

class TVShowRecommendationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = TVShowRecommendation
        fields = ["id", "username", "tvshow_id", "recommended_tv_show_id", "created_at"]
        read_only_fields = ["id", "username", "created_at"]

class TopRatedMovieSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    overview = serializers.CharField()
    release_date = serializers.CharField()
    rating = serializers.FloatField()
    poster_path = serializers.CharField(allow_null=True)

class FavoriteMovieSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = FavoriteMovie
        fields = ["id", "user", "movie_id", "movie_title", "added_at"]
        read_only_fields = ["id", "user", "added_at"]

class TopRatedTVShowSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    overview = serializers.CharField()
    first_air_date = serializers.CharField()
    poster_path = serializers.CharField(allow_null=True)
    vote_average = serializers.FloatField()

class TVShowCustomizationSerializer(serializers.Serializer):
    preferred_genres = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of preferred genres (e.g., ['Drama', 'Comedy'])"
    )
    min_rating = serializers.FloatField(required=False, help_text="Minimum rating (0-10)")
    release_year = serializers.IntegerField(required=False, help_text="Filter by release year")

class CustomizedTopRatedTVShowSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    overview = serializers.CharField()
    first_air_date = serializers.CharField()
    poster_path = serializers.CharField(allow_null=True)
    vote_average = serializers.FloatField()
    genres = serializers.ListField(child=serializers.CharField(), required=False)

class CastSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    character = serializers.CharField()
    profile_path = serializers.CharField(allow_null=True)

class CrewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    job = serializers.CharField()
    profile_path = serializers.CharField(allow_null=True)

class MovieCastAndCrewSerializer(serializers.Serializer):
    movie_title = serializers.CharField()  # Include movie title in the response
    cast = CastSerializer(many=True)
    crew = CrewSerializer(many=True)

class FavoriteActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteActor
        fields = ['id', 'actor_id', 'actor_name', 'profile_path', 'added_at']

class ActorMovieSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    title = serializers.CharField()
    release_date = serializers.CharField()
    character = serializers.CharField()
    poster_path = serializers.CharField(allow_null=True)

class ActorSerializer(serializers.Serializer):
    person_id = serializers.IntegerField()
    name = serializers.CharField()
    movies = ActorMovieSerializer(many=True)

class WatchProviderSerializer(serializers.Serializer):
    provider_name = serializers.CharField()
    logo_path = serializers.CharField(allow_null=True)