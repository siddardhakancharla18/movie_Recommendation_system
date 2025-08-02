import streamlit as st
import pickle
import pandas as pd
import requests

import time

def fetch_poster_by_movie_id(movie_id, retries=3, delay=1):
    api_key = "c8eebba7aafe893313aac88e7c437527"
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get('poster_path'):
                return "https://image.tmdb.org/t/p/w500" + data['poster_path']
            else:
                break  # No poster found in data
        except requests.exceptions.RequestException:
            if attempt == retries:
                # Suppress repeated warnings, show only once
                st.warning(f"Could not fetch poster for movie ID {movie_id}. Showing default image.")
            time.sleep(0.3)
    
    # Fallback image
    return "https://via.placeholder.com/300x450?text=No+Poster"




# --- Recommend movies ---
def recommend(movie):
    movie = movie.lower()
    index_data = movies[movies['title'].str.lower() == movie]
    if index_data.empty:
        st.error(f"❌ Movie '{movie}' not found in the dataset.")
        return [], []

    index = index_data.index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movies = []
    recommended_posters = []

    for i in distances[1:6]:  # Top 5 recommendations excluding the selected one
        row = movies.iloc[i[0]]
        movie_id = row['movie_id']  # ✅ Your pickle must contain this column
        title = row['title']
        poster = fetch_poster_by_movie_id(movie_id)

        recommended_movies.append(title)
        recommended_posters.append(poster)

    return recommended_movies, recommended_posters

# --- Load data ---
movies_list = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- Streamlit UI ---
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")

option = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(option)
    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.header(names[i])
                st.image(posters[i])
