import requests
import pymongo
from bson.objectid import ObjectId

# TMDB API Key
TMDB_API_KEY = '9c1fb0636dda039e31bdd33126a95b31'

# MongoDB Connection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['soundscene_db']
movies_collection = db['movies']


def fetch_genres():
    try:
        response = requests.get(f'https://api.themoviedb.org/3/genre/movie/list', params={'api_key': TMDB_API_KEY})
        response.raise_for_status()
        genres = response.json().get('genres', [])
        for genre in genres:
            db.genres.update_one(
                {"id": genre['id']},
                {"$set": genre},
                upsert=True
            )
        print("Genres fetched and stored successfully.")
    except requests.RequestException as e:
        print(f"Error fetching genres: {e}")


def fetch_movie_details(movie_id):
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}',
                                params={'api_key': TMDB_API_KEY, 'append_to_response': 'credits,keywords'})
        response.raise_for_status()
        movie_details = response.json()

        # Extracting required details
        cast = [member['name'] for member in
                movie_details.get('credits', {}).get('cast', [])[:10]]  # Top 10 cast members
        director = next((member['name'] for member in movie_details.get('credits', {}).get('crew', []) if
                         member['job'] == 'Director'), 'Unknown')
        production_companies = [company['name'] for company in movie_details.get('production_companies', [])]
        keywords = [keyword['name'] for keyword in movie_details.get('keywords', {}).get('keywords', [])]
        certification = 'Unknown'  # Default to Unknown if not found

        # Fetch certifications
        response_cert = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/release_dates',
                                     params={'api_key': TMDB_API_KEY})
        response_cert.raise_for_status()
        release_dates = response_cert.json().get('results', [])
        for country in release_dates:
            if country['iso_3166_1'] == 'US':
                for release in country['release_dates']:
                    if 'certification' in release and release['certification']:
                        certification = release['certification']
                        break

        return {
            'cast': cast,
            'director': director,
            'production_companies': production_companies,
            'keywords': keywords,
            'certification': certification,
            'budget': movie_details.get('budget', 0),
            'runtime': movie_details.get('runtime', 0)
        }
    except requests.RequestException as e:
        print(f"Error fetching movie details: {e}")
        return {}


def fetch_movies(page=1):
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/popular',
                                params={'api_key': TMDB_API_KEY, 'page': page})
        response.raise_for_status()
        movies = response.json().get('results', [])
        for movie in movies:
            movie_details = fetch_movie_details(movie['id'])
            movie_data = {
                'title': movie['title'],
                'release_year': int(movie['release_date'][:4]) if movie.get('release_date') else None,
                'rating': movie.get('vote_average'),
                'backdrop_url': f"https://image.tmdb.org/t/p/w500{movie['backdrop_path']}" if movie.get(
                    'backdrop_path') else None,
                'overview': movie.get('overview'),
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get(
                    'poster_path') else None,
                'duration': movie_details.get('runtime', 0),
                'language': movie.get('original_language'),
                'genres': movie.get('genre_ids', []),
                'mood': "N/A",  # Placeholder for mood, adjust as necessary
                'certification': movie_details.get('certification', 'Unknown'),
                'cast': movie_details.get('cast', []),
                'director': movie_details.get('director', 'Unknown'),
                'production_companies': movie_details.get('production_companies', []),
                'keywords': movie_details.get('keywords', []),
                'budget': movie_details.get('budget', 0)
            }
            movies_collection.update_one(
                {"id": movie['id']},
                {"$set": movie_data},
                upsert=True
            )
        print(f"Page {page} movies fetched and stored successfully.")
    except requests.RequestException as e:
        print(f"Error fetching movies: {e}")


if __name__ == '__main__':
    fetch_genres()
    for page in range(151, 250):  # Adjust the range for more pages if necessary
        fetch_movies(page)

    client.close()
