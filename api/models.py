from django.db import models
from django.contrib.auth.models import User

class RecentSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate searches with users
    movie_title = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)  # Timestamp for search

class RecentTVShowSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tv_show_title = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched for {self.tv_show_title}"

class MovieFeedback(models.Model):
    movie_title = models.CharField(max_length=255)  # Store the movie title
    rating = models.CharField(max_length=1, choices=[("0", "Dislike"), ("1", "Like")], default="0")  # Store rating as a string
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Link feedback to the authenticated user
    created_at = models.DateTimeField(auto_now_add=True)  # Rename field to created_at

    def __str__(self):
        return f"Feedback for '{self.movie_title}' by {self.user.username}"

class TVShowPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_genres = models.JSONField(default=list)  # Store genre names as a list

    def __str__(self):
        return f"Preferences of {self.user.username}"

class MovieRecommendationFeedback(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    FEEDBACK_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.IntegerField()
    recommended_movie_id = models.IntegerField()
    feedback = models.CharField(max_length=10, choices=FEEDBACK_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie_id', 'recommended_movie_id')

    def __str__(self):
        return f"{self.user.username} - {self.recommended_movie_id} ({self.feedback})"

class TVShowRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tvshow_id = models.IntegerField()  # The original TV show the recommendation is based on
    recommended_tv_show_id = models.IntegerField()  # The recommended TV show
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tvshow_id', 'recommended_tv_show_id')

    def __str__(self):
        return f"{self.user.username} recommends {self.recommended_tv_show_id} for {self.tvshow_id}"
    
class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie_id')

    def __str__(self):
        return f"{self.user.username} - {self.movie_title}"

class FavoriteActor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    actor_id = models.IntegerField()  # Actor's ID from TMDb
    actor_name = models.CharField(max_length=255)
    profile_path = models.URLField(null=True, blank=True)  # Optional actor image
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'actor_id')  # Prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} - {self.actor_name}"

class MovieWatchlist(models.Model):
    """Model to store a user's watchlisted movies."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    movie_id = models.IntegerField()  # TMDb movie ID
    movie_title = models.CharField(max_length=255)  # Store movie title
    poster_path = models.URLField(null=True, blank=True)  # Optional movie poster
    added_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    class Meta:
        unique_together = ('user', 'movie_id')  # Prevent duplicate entries

    def __str__(self):
        return f"{self.user.username} - {self.movie_title} (ID: {self.movie_id})"