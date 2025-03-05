from django.urls import path
from .views import RegisterView, LoginView, MovieSearchView, SaveRecentSearchView, TVShowSearchView, ClearRecentTVShowSearchView
from .views import TrendingMoviesView, SubmitMovieFeedbackView, TrendingTVShowsView, TVShowPreferenceView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('movies/search/', MovieSearchView.as_view(), name='movie-search'),  # Fixed path
    path('movies/search/save/', SaveRecentSearchView.as_view(), name='save-recent-search'),
    path("tvshows/search/", TVShowSearchView.as_view(), name="tvshow-search"),
    path('tvshows/search/clear/', ClearRecentTVShowSearchView.as_view(), name='clear-tvshow-searches'),
    path('movies/trending/', TrendingMoviesView.as_view(), name='trending-movies'),
    path('movies/trending/feedback/', SubmitMovieFeedbackView.as_view(), name='submit_movie_feedback'),
    path('tvshows/trending/', TrendingTVShowsView.as_view(), name='trending-tv-shows'),
    path('tvshows/trending/preferences/', TVShowPreferenceView.as_view(), name='tvshow-preferences'),
]
