from django.urls import path
from .views import RegisterView, LoginView, MovieSearchView, SaveRecentSearchView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('movies/search/', MovieSearchView.as_view(), name='movie-search'),  # Fixed path
    path('movies/search/save/', SaveRecentSearchView.as_view(), name='save-recent-search'),
]
