from django.shortcuts import render
import pandas as pd
import pickle
import requests
import streamlit as st
import os


# Get the base directory of the Django project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load the saved model components
model_dir = os.path.join(BASE_DIR, 'models')
with open(os.path.join(model_dir, 'tfidf_vectorizer.pkl'), 'rb') as file:
    tfidf_vectorizer = pickle.load(file)

with open(os.path.join(model_dir, 'cosine_sim.pkl'), 'rb') as file:
    cosine_sim = pickle.load(file)

with open(os.path.join(model_dir, 'movie_indices.pkl'), 'rb') as file:
    indices = pickle.load(file)

# TMDb API Key
api_key = "8265bd1679663a7ea12ac168da84d2e8"  # Replace with your TMDb API key


# Specify the path to the CSV file
csv_file_path = os.path.join(BASE_DIR, 'datasets', 'Movies_dataset.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)


# Load the dataset (make sure the file path matches your actual dataset)
df = pd.read_csv('C://Users//HP/ask movies recommender//Movies_dataset.csv')

def home(request):
    if request.method == 'POST':
        selected_movie = request.POST.get('selected_movie')
        recommended_movies = get_recommendations(selected_movie)
        if recommended_movies is not None:
            recommended_movies = recommended_movies.to_dict('records')  # Convert DataFrame to list of dictionaries
            movie_poster_urls = {movie['title']: get_movie_poster_url_tmdb(movie['title'], api_key) for movie in recommended_movies}
            return render(request, 'results.html', {'selected_movie': selected_movie, 'recommended_movies': recommended_movies, 'movie_poster_urls': movie_poster_urls})
    return render(request, 'home.html', {'movies': df['title'].tolist()})  # Pass list of movie titles to template

def get_recommendations(title):
    if title in indices:
        idx = indices[title]
        sim_scores = list(enumerate(cosine_sim[idx]))
        # Filter out movies with NaN similarity scores
        sim_scores = [score for score in sim_scores if not pd.isna(score[1])]
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]  # Get the top 10 most similar movies
        movie_indices = [i[0] for i in sim_scores]
        return df.iloc[movie_indices]
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no recommendations are found

def get_movie_poster_url_tmdb(movie_title, api_key):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
        response = requests.get(url)
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            movie_id = data['results'][0]['id']
            poster_url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={api_key}"
            response = requests.get(poster_url)
            data = response.json()
            if 'posters' in data and len(data['posters']) > 0:
                poster_path = data['posters'][0]['file_path']
                poster_url = f"https://image.tmdb.org/t/p/w300{poster_path}"
                print(f"Poster URL for {movie_title}: {poster_url}")  # Add this line for debugging
                return poster_url  # Adjust the size here
        return None
    except Exception as e:
        print(f"Error retrieving poster URL for {movie_title}: {e}")  # Add this line for debugging
        return None

