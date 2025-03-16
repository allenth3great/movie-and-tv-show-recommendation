import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import MovieFeedback, MovieRecommendationFeedback, TVShowRecommendation, FavoriteMovie

TV_GENRES = {
    "Action & Adventure": 10759,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Documentary": 99,
    "Drama": 18,
    "Family": 10751,
    "Kids": 10762,
    "Mystery": 9648,
    "News": 10763,
    "Reality": 10764,
    "Sci-Fi & Fantasy": 10765,
    "Soap": 10766,
    "Talk": 10767,
    "War & Politics": 10768,
    "Western": 37
}


def get_tokens_for_user(user):
    """Generate JWT tokens for the user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def search_movies_by_title(query):
    """Search movies by title using the TMDb API."""
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': query,
        'language': 'en-US',
        'page': 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        data = response.json()
        
        if "results" in data:
            return [
                {
                    "id": movie["id"],
                    "title": movie["title"],
                    "overview": movie.get("overview", "No description available."),
                    "release_date": movie.get("release_date", "Unknown"),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
                }
                for movie in data["results"]
            ]
        return {"error": "No results found."}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to TMDb API: {str(e)}"}
    
def search_tv_shows_by_title(query):
    """Search TV shows by title using the TMDb API."""
    url = "https://api.themoviedb.org/3/search/tv"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': query,
        'language': 'en-US',
        'page': 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        data = response.json()
        
        if "results" in data:
            return [
                {
                    "id": show["id"],
                    "title": show["name"],  # TMDb uses "name" for TV shows
                    "overview": show.get("overview", "No description available."),
                    "first_air_date": show.get("first_air_date", "Unknown"),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{show['poster_path']}" if show.get("poster_path") else None
                }
                for show in data["results"]
            ]
        return {"error": "No results found."}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to TMDb API: {str(e)}"}
    
def get_trending_movies():
    """Fetch trending movies from the TMDb API."""
    url = "https://api.themoviedb.org/3/trending/movie/week"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for HTTP 4xx/5xx responses
        data = response.json()

        if "results" in data:
            return [
                {
                    "id": movie["id"],
                    "title": movie["title"],
                    "overview": movie.get("overview", "No description available."),
                    "release_date": movie.get("release_date", "Unknown"),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
                }
                for movie in data["results"]
            ]
        return {"error": "No trending movies found."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to TMDb API: {str(e)}"}
    
def submit_movie_feedback(movie_title, rating, comment, user):
    try:
        feedback = MovieFeedback.objects.create(
            movie_title=movie_title,
            rating=rating,
            comment=comment,
            user=user
        )
        return feedback
    except Exception as e:
        return None
    
def get_trending_tv_shows():
    """Fetch trending TV shows from TMDb API."""
    url = "https://api.themoviedb.org/3/trending/tv/week"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        data = response.json()

        if "results" in data:
            return [
                {
                    "id": tv_show["id"],
                    "title": tv_show["name"],
                    "overview": tv_show.get("overview", "No description available."),
                    "first_air_date": tv_show.get("first_air_date", "Unknown"),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{tv_show['poster_path']}" if tv_show.get("poster_path") else None
                }
                for tv_show in data["results"]
            ]
        return {"error": "No results found."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to TMDb API: {str(e)}"}
    
def get_movie_title(movie_id):
    """Fetch the movie title from TMDb based on the given movie_id."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("title", "Unknown Movie")
    except requests.exceptions.RequestException:
        return None  # Return None if the movie is not found

def get_movie_recommendations(movie_id):
    """Fetch recommended movies based on a given movie ID from the TMDb API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        recommendations = [
            {
                "id": movie["id"],
                "title": movie["title"],
                "overview": movie.get("overview", "No description available."),
                "release_date": movie.get("release_date", "Unknown"),
                "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
            }
            for movie in data.get("results", [])
        ]

        return recommendations if recommendations else None
    
    except requests.exceptions.RequestException:
        return None
    
def fetch_movie_title(movie_id):
    """Fetch movie title from TMDb API based on movie ID."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": settings.TMDB_API_KEY, "language": "en-US"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data.get("title", "Unknown Title")
    except requests.RequestException:
        return "Unknown Title"

def save_feedback(user, movie_id, recommended_movie_id, feedback):
    """Save user feedback on recommended movies."""
    feedback_instance, created = MovieRecommendationFeedback.objects.update_or_create(
        user=user,
        movie_id=movie_id,
        recommended_movie_id=recommended_movie_id,
        defaults={"feedback": feedback}
    )
    return feedback_instance

def get_tv_show_recommendations(tv_show_id):
    """Fetch recommended TV shows based on a given TV show ID from the TMDb API."""
    url = f"https://api.themoviedb.org/3/tv/{tv_show_id}/recommendations"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
        'page': 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if "results" in data and data["results"]:
            return [
                {
                    "id": show["id"],
                    "title": show.get("name", "Unknown Title"),
                    "overview": show.get("overview", "No description available."),
                    "first_air_date": show.get("first_air_date", "Unknown"),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{show['poster_path']}" if show.get("poster_path") else None
                }
                for show in data["results"]
            ]
        return {"error": "No recommendations found."}
    except requests.RequestException as e:
        return {"error": f"Error connecting to TMDb API: {str(e)}"}
    
def fetch_tv_show_title(tv_show_id):
    """Fetch the title of a TV show by its ID from the TMDb API."""
    url = f"https://api.themoviedb.org/3/tv/{tv_show_id}"
    params = {'api_key': settings.TMDB_API_KEY, 'language': 'en-US'}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json()
        return data.get("name", "Unknown Title")
    except requests.RequestException:
        return "Unknown Title"

def save_tv_show_recommendation(user, tvshow_id, recommended_tv_show_id):
    """Save a TV show recommendation for a user."""
    recommendation, created = TVShowRecommendation.objects.get_or_create(
        user=user,
        tvshow_id=tvshow_id,
        recommended_tv_show_id=recommended_tv_show_id
    )
    return recommendation, created

def remove_tv_show_recommendation(user, tv_show_id, recommended_tv_show_id):
    """
    Remove a specific TV show recommendation.
    """
    try:
        recommendation = TVShowRecommendation.objects.get(
            user=user,
            tvshow_id=tv_show_id,
            recommended_tv_show_id=recommended_tv_show_id
        )
        recommendation.delete()
        return {"message": "Recommendation removed successfully."}
    except TVShowRecommendation.DoesNotExist:
        return {"error": "Recommendation not found."}

def get_top_rated_movies():
    """Fetch the top-rated movies from the TMDb API."""
    url = "https://api.themoviedb.org/3/movie/top_rated"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
        'page': 1  # Fetch the first page
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "results" in data:
            return [
                {
                    "id": movie["id"],
                    "title": movie["title"],
                    "overview": movie.get("overview", "No description available."),
                    "release_date": movie.get("release_date", "Unknown"),
                    "rating": movie.get("vote_average", "N/A"),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
                }
                for movie in data["results"]
            ]
        return {"error": "No top-rated movies found."}
    except requests.RequestException as e:
        return {"error": f"Error fetching top-rated movies: {str(e)}"}

def add_favorite_movie(user, movie_id, movie_title):
    """Adds a movie to the user's favorite list."""
    favorite, created = FavoriteMovie.objects.get_or_create(
        user=user,
        movie_id=movie_id,
        defaults={"movie_title": movie_title}
    )

    if created:
        return {"message": f"'{movie_title}' added to favorites."}
    return {"message": f"'{movie_title}' is already in favorites."}