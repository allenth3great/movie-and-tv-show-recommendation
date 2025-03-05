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