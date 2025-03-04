from django.contrib.auth.models import User
from rest_framework import serializers
from .models import RecentSearch
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
    

