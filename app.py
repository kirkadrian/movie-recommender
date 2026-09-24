import streamlit as st
import pickle

with open('movies_list.pkl', 'rb') as f:
    movies_df = pickle.load(f)

with open('content_recommendations.pkl', 'rb') as f:
    content_recs = pickle.load(f)

with open('collaborative_predictions.pkl', 'rb') as f:
    predictions_df = pickle.load(f)

with open('user_history.pkl', 'rb') as f:
    user_history = pickle.load(f)

movie_titles = movies_df['title'].tolist()
valid_users = predictions_df.index.tolist()

st.title("Movie Recommendation Engine")

# --- Content-Based Filtering Section ---
st.header("Content-Based Filtering")
st.write("Find similar movies based on genre and metadata.")

selected_movie = st.selectbox("Search for a movie you like:", movie_titles)

if st.button("Get Content Recommendations"):
    recommendations = content_recs.get(selected_movie, [])
    st.write(f"Because you liked **{selected_movie}**, we recommend:")
    for title in recommendations:
        st.write(f"- {title}")

st.divider()

# --- Collaborative Filtering Section ---
st.header("Collaborative Filtering")
st.write("Discover movies based on hidden taste patterns from users like you.")

selected_user = st.selectbox("Select a User ID:", valid_users)

if st.button("Get Collaborative Recommendations"):
    user_predictions = predictions_df.loc[selected_user].sort_values(ascending=False)
    seen_movies = user_history.get(selected_user, [])
    recommendations = user_predictions.drop(seen_movies, errors='ignore').head(5).index.tolist()
    
    st.write(f"Top personalized recommendations for User **{selected_user}**:")
    for title in recommendations:
        st.write(f"- {title}")