from django.db import models
from django.contrib.auth.models import User

class RecentSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    movie_title = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)  

class RecentTVShowSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tv_show_title = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched for {self.tv_show_title}"

class MovieFeedback(models.Model):
    movie_title = models.CharField(max_length=255)  
    rating = models.CharField(max_length=1, choices=[("0", "Dislike"), ("1", "Like")], default="0")  
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Feedback for '{self.movie_title}' by {self.user.username}"

class TVShowPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_genres = models.JSONField(default=list)  

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
    tvshow_id = models.IntegerField()  
    recommended_tv_show_id = models.IntegerField()  
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
    actor_id = models.IntegerField()  
    actor_name = models.CharField(max_length=255)
    profile_path = models.URLField(null=True, blank=True)  
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'actor_id')  

    def __str__(self):
        return f"{self.user.username} - {self.actor_name}"

class MovieWatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    movie_id = models.IntegerField()  
    movie_title = models.CharField(max_length=255)  
    poster_path = models.URLField(null=True, blank=True)  
    added_at = models.DateTimeField(auto_now_add=True)  

    class Meta:
        unique_together = ('user', 'movie_id')  

    def __str__(self):
        return f"{self.user.username} - {self.movie_title} (ID: {self.movie_id})"