import streamlit as st
import pickle
import random

st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
    }
    
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, label, div, span, li {
        color: #000000 !important;
        font-family: 'Tahoma', sans-serif !important;
    }
    
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 4px !important;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton>button:hover {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 4px !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: #000000 !important;
        box-shadow: none !important;
    }
    
    .stSelectbox div[data-baseweb="select"] span, 
    .stSelectbox div[data-baseweb="select"] input {
        color: #000000 !important;
        background-color: transparent !important;
    }
    
    .stSelectbox svg {
        fill: #000000 !important;
    }
    
    div[data-baseweb="popover"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #000000 !important;
    }
    
    div[data-baseweb="popover"] ul {
        background-color: #FFFFFF !important;
    }
    
    div[data-baseweb="popover"] li {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    div[data-baseweb="popover"] li:hover {
        background-color: #E0E0E0 !important;
        color: #000000 !important;
    }
    
    hr {
        border-top: 1px solid #E0E0E0 !important;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

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

selected_user = st.selectbox("Select a User ID:", valid_users, key="user_dropdown")

col1, col2 = st.columns(2)

with col1:
    if st.button("Get Collaborative Recommendations"):
        user_predictions = predictions_df.loc[selected_user].sort_values(ascending=False)
        seen_movies = user_history.get(selected_user, [])
        st.session_state.collab_results = user_predictions.drop(seen_movies, errors='ignore').head(5).index.tolist()
        st.session_state.collab_user = selected_user

with col2:
    st.button("Random User", on_click=pick_random_user)

if st.session_state.collab_results:
    st.write(f"Recommendations from User **{st.session_state.collab_user}**:")
    for title in st.session_state.collab_results:
        st.write(f"- {title}")