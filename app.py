import streamlit as st
import pickle

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

st.title("Movie Recommendation Engine")

st.header("Content-Based Filtering")
st.write("Find similar movies based on genre and metadata.")

selected_movie = st.selectbox("Search for a movie you like:", movie_titles)

if st.button("Get Content Recommendations"):
    recommendations = content_recs.get(selected_movie, [])
    st.write(f"Because you liked **{selected_movie}**, we recommend:")
    for title in recommendations:
        st.write(f"- {title}")

st.divider()

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