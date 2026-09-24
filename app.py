import streamlit as st
import pickle
import random

@st.cache_data
def load_data():
    with open('movies_list.pkl', 'rb') as f:
        movies = pickle.load(f)
    with open('content_recommendations.pkl', 'rb') as f:
        content = pickle.load(f)
    with open('collaborative_predictions.pkl', 'rb') as f:
        collab = pickle.load(f)
    with open('user_history.pkl', 'rb') as f:
        history = pickle.load(f)
    return movies, content, collab, history

movies_df, content_recs, predictions_df, user_history = load_data()

movie_titles = movies_df['title'].tolist()
valid_users = predictions_df.index.tolist()

if 'content_results' not in st.session_state:
    st.session_state.content_results = []
if 'content_movie' not in st.session_state:
    st.session_state.content_movie = ""
if 'collab_results' not in st.session_state:
    st.session_state.collab_results = []
if 'collab_user' not in st.session_state:
    st.session_state.collab_user = ""
if 'user_dropdown' not in st.session_state:
    st.session_state.user_dropdown = valid_users[0]

st.title("Movie Recommendation Engine")

st.header("Content-Based Filtering")
st.write("Find similar movies based on genre and metadata.")

selected_movie = st.selectbox("Search for a movie you personally like:", movie_titles)

if st.button("Get Content Recommendations"):
    st.session_state.content_results = content_recs.get(selected_movie, [])
    st.session_state.content_movie = selected_movie

if st.session_state.content_results:
    st.write(f"Because you liked **{st.session_state.content_movie}**, based on the model we recommend:")
    for title in st.session_state.content_results:
        st.write(f"- {title}")

st.divider()

st.header("Collaborative Filtering")
st.write("Discover different movies based on other user's favorite movies.")

def pick_random_user():
    st.session_state.user_dropdown = random.choice(valid_users)

col1, col2 = st.columns([3, 1])

with col1:
    selected_user = st.selectbox("Select a User ID:", valid_users, key="user_dropdown")

with col2:

    st.write("")
    st.write("")
    st.button("Random User", on_click=pick_random_user)

if st.button("Get Collaborative Recommendations"):
    user_predictions = predictions_df.loc[selected_user].sort_values(ascending=False)
    seen_movies = user_history.get(selected_user, [])
    st.session_state.collab_results = user_predictions.drop(seen_movies, errors='ignore').head(5).index.tolist()
    st.session_state.collab_user = selected_user


if st.session_state.collab_results:
    st.write(f"Recommendations from User **{st.session_state.collab_user}**:")
    for title in st.session_state.collab_results:
        st.write(f"- {title}")