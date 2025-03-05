from django.contrib.auth.models import User
from rest_framework import serializers
from .models import RecentSearch, MovieFeedback
from django.utils.timezone import localtime

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

