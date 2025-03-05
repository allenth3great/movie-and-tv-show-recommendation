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

