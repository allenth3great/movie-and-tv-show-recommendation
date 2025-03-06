import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import MovieFeedback

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
