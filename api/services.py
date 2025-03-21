import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import MovieFeedback, MovieRecommendationFeedback, TVShowRecommendation, FavoriteMovie, FavoriteActor, MovieWatchlist

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

TV_SHOW_GENRES = {
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
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def search_movies_by_title(query):   
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': query,
        'language': 'en-US',
        'page': 1
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
                    "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
                }
                for movie in data["results"]
            ]
        return {"error": "No results found."}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to TMDb API: {str(e)}"}
    
def search_tv_shows_by_title(query):    
    url = "https://api.themoviedb.org/3/search/tv"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': query,
        'language': 'en-US',
        'page': 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
        data = response.json()
        
        if "results" in data:
            return [
                {
                    "id": show["id"],
                    "title": show["name"],  
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
    url = "https://api.themoviedb.org/3/trending/movie/week"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US'
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
    url = "https://api.themoviedb.org/3/trending/tv/week"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
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
        return None  

def get_movie_recommendations(movie_id):   
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
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": settings.TMDB_API_KEY, "language": "en-US"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
        data = response.json()
        return data.get("title", "Unknown Title")
    except requests.RequestException:
        return "Unknown Title"

def save_feedback(user, movie_id, recommended_movie_id, feedback):
    feedback_instance, created = MovieRecommendationFeedback.objects.update_or_create(
        user=user,
        movie_id=movie_id,
        recommended_movie_id=recommended_movie_id,
        defaults={"feedback": feedback}
    )
    return feedback_instance

def get_tv_show_recommendations(tv_show_id):   
    url = f"https://api.themoviedb.org/3/tv/{tv_show_id}/recommendations"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
        'page': 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
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
    url = f"https://api.themoviedb.org/3/tv/{tv_show_id}"
    params = {'api_key': settings.TMDB_API_KEY, 'language': 'en-US'}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
        data = response.json()
        return data.get("name", "Unknown Title")
    except requests.RequestException:
        return "Unknown Title"

def fetch_tv_show_details(tv_show_id):
    api_key = settings.TMDB_API_KEY
    url = f"https://api.themoviedb.org/3/tv/{tv_show_id}?api_key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    
    return {}

def save_tv_show_recommendation(user, tvshow_id, recommended_tv_show_id):   
    recommendation, created = TVShowRecommendation.objects.get_or_create(
        user=user,
        tvshow_id=tvshow_id,
        recommended_tv_show_id=recommended_tv_show_id
    )
    return recommendation, created

def remove_tv_show_recommendation(user, tv_show_id, recommended_tv_show_id):    
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
    url = "https://api.themoviedb.org/3/movie/top_rated"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
        'page': 1  
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
    favorite, created = FavoriteMovie.objects.get_or_create(
        user=user,
        movie_id=movie_id,
        defaults={"movie_title": movie_title}
    )

    if created:
        return {"message": f"'{movie_title}' added to favorites."}
    return {"message": f"'{movie_title}' is already in favorites."}

def get_top_rated_tv_shows():    
    url = "https://api.themoviedb.org/3/tv/top_rated"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
        data = response.json()

        if "results" in data:
            return [
                {
                    "id": tv_show["id"],
                    "title": tv_show["name"],
                    "overview": tv_show.get("overview", "No description available."),
                    "first_air_date": tv_show.get("first_air_date", "Unknown"),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{tv_show['poster_path']}" if tv_show.get("poster_path") else None,
                    "vote_average": tv_show.get("vote_average", 0)
                }
                for tv_show in data["results"]
            ]
        return {"error": "No results found."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to TMDb API: {str(e)}"}

def get_customized_top_rated_tv_shows(preferred_genres=None, min_rating=None, release_year=None):
    url = "https://api.themoviedb.org/3/tv/top_rated"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "results" not in data:
            return {"error": "No results found."}

        filtered_tv_shows = []
        for show in data["results"]:
            
            show_genre_ids = set(show.get("genre_ids", []))
            genre_filter = True  

            if preferred_genres:
                selected_genre_ids = {TV_SHOW_GENRES.get(genre) for genre in preferred_genres if genre in TV_SHOW_GENRES}
                genre_filter = bool(show_genre_ids & selected_genre_ids)  

            rating_filter = min_rating is None or show.get("vote_average", 0) >= min_rating
            year_filter = release_year is None or (show.get("first_air_date", "").startswith(str(release_year)))

            if genre_filter and rating_filter and year_filter:
                filtered_tv_shows.append({
                    "id": show["id"],
                    "title": show["name"],
                    "overview": show.get("overview", "No description available."),
                    "first_air_date": show.get("first_air_date", "Unknown"),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{show['poster_path']}" if show.get("poster_path") else None,
                    "vote_average": show.get("vote_average", 0),
                    "genres": [genre for genre, genre_id in TV_SHOW_GENRES.items() if genre_id in show_genre_ids]
                })

        return filtered_tv_shows if filtered_tv_shows else {"error": "No TV shows match your criteria."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to TMDb API: {str(e)}"}

def get_movie_details_and_cast(movie_id):
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US'
    }

    try:
        
        details_response = requests.get(details_url, params=params)
        details_response.raise_for_status()
        details_data = details_response.json()

        
        credits_response = requests.get(credits_url, params=params)
        credits_response.raise_for_status()
        credits_data = credits_response.json()

        if "title" not in details_data or "cast" not in credits_data or "crew" not in credits_data:
            return {"error": "No movie details, cast, or crew information found."}

        
        movie_title = details_data["title"]

        
        cast = [
            {
                "id": member["id"],
                "name": member["name"],
                "character": member.get("character", "Unknown"),
                "profile_path": f"https://image.tmdb.org/t/p/w500{member['profile_path']}" if member.get("profile_path") else None
            }
            for member in credits_data["cast"][:10]
        ]

        
        crew = [
            {
                "id": member["id"],
                "name": member["name"],
                "job": member["job"],
                "profile_path": f"https://image.tmdb.org/t/p/w500{member['profile_path']}" if member.get("profile_path") else None
            }
            for member in credits_data["crew"] if member["job"] in ["Director", "Producer", "Writer"]
        ]

        return {
            "movie_title": movie_title,
            "cast": cast,
            "crew": crew
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to TMDb API: {str(e)}"}

def add_favorite_actor(user, actor_id, actor_name, profile_path=None):    
    favorite, created = FavoriteActor.objects.get_or_create(
        user=user,
        actor_id=actor_id,
        defaults={"actor_name": actor_name, "profile_path": profile_path}
    )
    return favorite, created

TMDB_BASE_URL = "https://api.themoviedb.org/3"

def get_actor_movies(person_id):       
    person_url = f"{TMDB_BASE_URL}/person/{person_id}"
    credits_url = f"{TMDB_BASE_URL}/person/{person_id}/movie_credits"
    
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US"
    }

    person_response = requests.get(person_url, params=params)
    credits_response = requests.get(credits_url, params=params)

    if person_response.status_code != 200 or credits_response.status_code != 200:
        return None  

    person_data = person_response.json()
    credits_data = credits_response.json()

    return {
        "person_id": person_id,
        "name": person_data.get("name", "Unknown"),
        "movies": [
            {
                "movie_id": movie["id"],
                "title": movie["title"],
                "release_date": movie.get("release_date", "N/A"),
                "character": movie.get("character", "Unknown"),
                "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
            }
            for movie in credits_data.get("cast", [])  
        ]
    
    }

def remove_favorite_actor(user, actor_id):    
    try:
        favorite_actor = FavoriteActor.objects.get(user=user, actor_id=actor_id)
        favorite_actor.delete()
        return True
    except FavoriteActor.DoesNotExist:
        return False
    
def get_movie_details_and_watch_providers(movie_id):    
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    providers_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"

    params = {"api_key": settings.TMDB_API_KEY, "language": "en-US"}

    details_response = requests.get(details_url, params=params)
    providers_response = requests.get(providers_url, params={"api_key": settings.TMDB_API_KEY})

    if details_response.status_code != 200:
        return None, None

    movie_data = details_response.json()
    movie_title = movie_data.get("title")

    if providers_response.status_code != 200:
        return movie_title, None

    providers_data = providers_response.json().get("results", {})

    return movie_title, providers_data 

def add_movie_to_watchlist(user, movie_id, movie_title, poster_path=None):
    watchlist_item, created = MovieWatchlist.objects.get_or_create(
        user=user,
        movie_id=movie_id,
        defaults={"movie_title": movie_title, "poster_path": poster_path}
    )
    return watchlist_item, created

def remove_movie_from_watchlist(user, movie_id):
    try:
        watchlist_item = MovieWatchlist.objects.get(user=user, movie_id=movie_id)
        watchlist_item.delete()
        return True
    except MovieWatchlist.DoesNotExist:
        return False