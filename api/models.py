from django.db import models
from django.contrib.auth.models import User

class RecentSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate searches with users
    movie_title = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)  # Timestamp for search

