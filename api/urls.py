from django.urls import path
from .views import RegisterView, LoginView, MovieSearchView, SaveRecentSearchView, TVShowSearchView, ClearRecentTVShowSearchView
from .views import TrendingMoviesView, SubmitMovieFeedbackView, TrendingTVShowsView, TVShowPreferenceView, MovieRecommendationsView, MovieRecommendationFeedbackView
from .views import TVShowRecommendationsView, SaveTVShowRecommendationView, RemoveTVShowRecommendationView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('movies/search/', MovieSearchView.as_view(), name='movie-search'),  
    path('movies/search/save/', SaveRecentSearchView.as_view(), name='save-recent-search'),
    path("tvshows/search/", TVShowSearchView.as_view(), name="tvshow-search"),
    path('tvshows/search/clear/', ClearRecentTVShowSearchView.as_view(), name='clear-tvshow-searches'),
    path('movies/trending/', TrendingMoviesView.as_view(), name='trending-movies'),
    path('movies/trending/feedback/', SubmitMovieFeedbackView.as_view(), name='submit_movie_feedback'),
    path('tvshows/trending/', TrendingTVShowsView.as_view(), name='trending-tv-shows'),
    path('tvshows/trending/preferences/', TVShowPreferenceView.as_view(), name='tvshow-preferences'),
    path('movies/<int:movie_id>/recommendations/', MovieRecommendationsView.as_view(), name='movie-recommendations'),
    path("movies/<int:movie_id>/recommendations/feedback/", MovieRecommendationFeedbackView.as_view(), name="movie-feedback"),
    path('tvshows/<int:tv_show_id>/recommendations/', TVShowRecommendationsView.as_view(), name='tvshow-recommendations'),
    path('tvshows/<int:tvShowId>/recommendations/save/', SaveTVShowRecommendationView.as_view(), name='save-tvshow-recommendation'),
    path("tvshows/<int:tvShowId>/recommendations/remove/", RemoveTVShowRecommendationView.as_view(), name="remove_tv_show_recommendation"),
]

