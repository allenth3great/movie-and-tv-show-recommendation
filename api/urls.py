from django.urls import path
from .views import RegisterView, LoginView, MovieSearchView, SaveRecentSearchView, TVShowSearchView, ClearRecentTVShowSearchView, CustomizeTopRatedTVShowsView, MovieCastView, RemoveFavoriteActorView
from .views import TrendingMoviesView, SubmitMovieFeedbackView, TrendingTVShowsView, TVShowPreferenceView, MovieRecommendationsView, MovieRecommendationFeedbackView, ActorMoviesView, MovieWatchProvidersView
from .views import TVShowRecommendationsView, SaveTVShowRecommendationView, RemoveTVShowRecommendationView, TopRatedMoviesView, AddFavoriteMovieView, TopRatedTVShowsView, AddFavoriteActorView

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
    path("movies/top-rated/", TopRatedMoviesView.as_view(), name="top_rated_movies"),
    path("movies/top-rated/favorites/", AddFavoriteMovieView.as_view(), name="add_favorite_movie"),
    path("tvshows/top-rated/", TopRatedTVShowsView.as_view(), name="top_rated_tv_shows"),
    path("tvshows/top-rated/customize/", CustomizeTopRatedTVShowsView.as_view(), name="customize_top_rated_tv_shows"),
    path('movies/<int:movie_id>/cast/', MovieCastView.as_view(), name='movie-cast'),
    path('movies/<int:movie_id>/cast/favorite/', AddFavoriteActorView.as_view(), name='add-favorite-actor'),
    path("person/<int:personId>/movies/", ActorMoviesView.as_view(), name="actor-movies"),
    path("person/<int:personId>/movies/remove/", RemoveFavoriteActorView.as_view(), name="remove_favorite_actor"),
    path("movies/<int:movieId>/watch-providers/", MovieWatchProvidersView.as_view(), name="movie_watch_providers"),

]

