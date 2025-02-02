# app/routes.py
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from .models import User

main = Blueprint('main', __name__)

@main.route('/')
def home():
    genre_map = {
        28: 'Action',
        16: 'Animation',
        12: 'Adventure',
        35: 'Comedy',
        27: 'Horror',
        14: 'Fantasy',
        10751: 'Family',
        10752: 'War',
        18: 'Drama',
        99: 'Documentary',
        878: 'Science Fiction',
        10749: 'Romance',
        80: 'Crime',
        36: 'History',
        37: 'Western',
        10770: 'TV Movie',
        53: 'Thriller',
        10402: 'Music',
        9648: 'Mystery'
    }

    movies = list(current_app.db.movies.find())
    movie_count = len(movies)
    
    if movie_count > 0:
        random_index = random.randint(0, movie_count - 1)
        random_movie = movies[random_index]
        
        # Convert genre IDs to names
        genre_ids = random_movie.get('genres', [])
        genre_names = [genre_map.get(genre_id, 'Unknown') for genre_id in genre_ids]

        movie_info = {
            'backdrop_url': random_movie.get('backdrop_url'),
            'overview': random_movie.get('overview'),
            'release_date': random_movie.get('release_year'),
            'title': random_movie.get('title'),
            'poster_url': random_movie.get('poster_url'),
            'rating': random_movie.get('rating'),
            'genres': genre_names  # Updated to use genre names
        }

        return render_template('SoundScene.html', movie=movie_info)
    
    else:
        return render_template('SoundScene.html', movie=None)


@main.route('/discover/movies', methods=['GET', 'POST'])
def discover_movies():
    if request.method == 'POST':
        genres = request.form.getlist('genres')
        certifications = request.form.getlist('certifications')
        language = request.form.get('language')
        cast = request.form.get('cast')
        director = request.form.get('director')
        keywords = request.form.getlist('keywords')
        production_companies = request.form.getlist('production_companies')
        vote_count = int(request.form.get('vote_count')) if request.form.get('vote_count') else None
        release_year_min = int(request.form.get('release_year_min')) if request.form.get('release_year_min') else 1900
        release_year_max = int(request.form.get('release_year_max')) if request.form.get('release_year_max') else 2100

        query = {}

        if genres:
            query['genres'] = {'$in': [int(genre) for genre in genres]}
        if certifications:
            query['certification'] = {'$in': certifications}
        if language:
            if language == 'en':
                query['language'] = 'en'
            else:
                query['language'] = {'$ne': 'en'}
        if cast:
            query['cast'] = {'$elemMatch': {'$regex': cast, '$options': 'i'}}
        if director:
            query['director'] = {'$regex': director, '$options': 'i'}
        if keywords:
            query['keywords'] = {'$in': keywords}
        if production_companies:
            query['production_companies'] = {'$elemMatch': {'$in': production_companies}}
        if vote_count is not None:
            query['vote_count'] = {'$gte': vote_count}
        query['release_year'] = {'$gte': release_year_min, '$lte': release_year_max}

        try:
            movies = list(current_app.db.movies.find(query).limit(100))
            print(f"Generated query: {query}")
            print(f"Found {len(movies)} movies")
            if not movies:
                flash('No movies found matching the criteria', 'warning')
                return redirect(url_for('main.discover_movies'))

            random.shuffle(movies)
            top_movies = movies[:random.randint(3, 5)]
            print(f"Top movies: {top_movies}")
            for movie in top_movies:
                movie['_id'] = str(movie['_id'])
            session['recommended_movies'] = top_movies

            return redirect(url_for('main.recommendation_result'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('main.discover_movies'))

    genres = current_app.db.genres.find()
    return render_template('DiscoverMovies.html', genres=genres)

@main.route('/recommendation_result')
def recommendation_result():
    movies = session.get('recommended_movies', [])
    return render_template('RecommendationResult.html', movies=movies)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = current_app.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            user_obj = User(user_id=user['_id'], email=user['email'], password=user['password'])
            login_user(user_obj)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        if current_app.db.users.find_one({'email': email}):
            flash('Email address already exists', 'danger')
        else:
            current_app.db.users.insert_one({
                'email': email,
                'password': hashed_password
            })
            flash('Registration successful!', 'success')
            return redirect(url_for('main.login'))

    return render_template('register.html')


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthday = request.form['birthday']
        favorite_movie = request.form['favorite_movie']
        favorite_band = request.form['favorite_band']
        picture = request.form['picture']

        current_app.db.users.update_one(
            {'email': email},
            {'$set': {
                'first_name': first_name,
                'last_name': last_name,
                'birthday': birthday,
                'favorite_movie': favorite_movie,
                'favorite_band': favorite_band,
                'picture': picture
            }}
        )
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.home'))

    return render_template('profile.html')


@main.route('/about')
def about():
    return render_template('About.html')


@main.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query', '').lower()
    movies = list(current_app.db.movies.find({"title": {"$regex": query, "$options": "i"}}))

    genre_map = {
        28: 'Action',
        16: 'Animation',
        12: 'Adventure',
        35: 'Comedy',
        27: 'Horror',
        14: 'Fantasy',
        10751: 'Family',
        10752: 'War',
        18: 'Drama',
        99: 'Documentary',
        878: 'Science Fiction',
        10749: 'Romance',
        80: 'Crime',
        36: 'History',
        37: 'Western',
        10770: 'TV Movie',
        53: 'Thriller',
        10402: 'Music',
        9648: 'Mystery'
    }

    # Update movies with genre names
    for movie in movies:
        genre_ids = movie.get('genre_ids', []) + movie.get('genres', [])
        movie['genres'] = [genre_map.get(genre_id, 'Unknown') for genre_id in set(genre_ids)]
        # Convert MongoDB Int and Double fields
        movie['release_year'] = int(movie.get('release_year', 0))
        movie['rating'] = float(movie.get('rating', 0))
        movie['duration'] = int(movie.get('duration', 0))

    return render_template('SearchResults.html', query=query, movies=movies)


@main.route('/discover/music', methods=['GET'])
def discover_music():
    return render_template('DiscoverMusic.html')


@main.route('/discover/community/music', methods=['GET'])
def discover_community_music():
    return render_template('DiscoverCommunityMusic.html')
