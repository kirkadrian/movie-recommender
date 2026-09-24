import streamlit as st
import pickle
import random
import requests
import re 

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", "")


@st.cache_data
def get_poster_url(title):
    if not TMDB_API_KEY:
        return None
    try:
        clean_title = re.sub(r'\s*\(\d{4}\)', '', title).strip()
        
        r = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": TMDB_API_KEY, "query": clean_title},
            timeout=5,
        )
        results = r.json().get("results", [])
        if results and results[0].get("poster_path"):
            return f"https://image.tmdb.org/t/p/w200{results[0]['poster_path']}"
    except Exception:
        pass
    return None

def show_poster_grid(titles):
    cols = st.columns(5)
    for i, title in enumerate(titles):
        with cols[i % 5]:
            poster = get_poster_url(title)
            if poster:
                st.image(poster, width='stretch')
            st.caption(title)

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

try:
    with st.spinner("Loading recommendation data..."):
        movies_df, content_recs, predictions_df, user_history = load_data()
except FileNotFoundError as e:
    st.error(
        f"Couldn't find a required data file ({e.filename}). "
        "Make sure all four .pkl files are present in the app directory."
    )
    st.stop()
except Exception as e:
    st.error(f"Something went wrong while loading data: {e}")
    st.stop()

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

def clear_content_results():
    st.session_state.content_results = []
    st.session_state.content_movie = ""

selected_movie = st.selectbox(
    "Search for a movie you personally like:",
    movie_titles,
    key="content_movie_dropdown",
    on_change=clear_content_results,
)

content_num_recs = st.select_slider(
    "Number of recommendations:",
    options=[5, 10, 15],
    value=5,
    key="content_num_recs",
    on_change=clear_content_results,
)

if st.button("Get Content Recommendations"):
    raw_recs = content_recs.get(selected_movie, [])
    
    clean_recs = [movie for movie in raw_recs if movie != selected_movie]
    
    st.session_state.content_results = clean_recs[:content_num_recs]
    st.session_state.content_movie = selected_movie

if st.session_state.content_movie:
    if st.session_state.content_results:
        st.write(f"Because you liked **{st.session_state.content_movie}**, based on the model we recommend:")
        show_poster_grid(st.session_state.content_results)
    else:
        st.info(f"No similar movies found for **{st.session_state.content_movie}**.")

st.divider()

st.header("Collaborative Filtering")
st.write("Discover different movies based on other user's favorite movies.")

def clear_collab_results():
    st.session_state.collab_results = []
    st.session_state.collab_user = ""

def pick_random_user():
    st.session_state.user_dropdown = random.choice(valid_users)
    clear_collab_results()

selected_user = st.selectbox(
    "Select a User ID:",
    valid_users,
    key="user_dropdown",
    on_change=clear_collab_results,
)

collab_num_recs = st.select_slider(
    "Number of recommendations:",
    options=[5, 10, 15],
    value=5,
    key="collab_num_recs",
    on_change=clear_collab_results,
)

col1, col2 = st.columns(2)

with col1:
    if st.button("Get Collaborative Recommendations"):
        try:
            user_predictions = predictions_df.loc[selected_user].sort_values(ascending=False)
            seen_movies = user_history.get(selected_user, [])
            st.session_state.collab_results = user_predictions.drop(seen_movies, errors='ignore').head(collab_num_recs).index.tolist()
            st.session_state.collab_user = selected_user
        except KeyError:
            st.error(f"No prediction data found for user {selected_user}.")

with col2:
    st.button("Random User", on_click=pick_random_user)

if st.session_state.collab_user:
    if st.session_state.collab_results:
        st.write(f"Recommendations from User **{st.session_state.collab_user}**:")
        show_poster_grid(st.session_state.collab_results)
    else:
        st.info(f"No new recommendations available for User **{st.session_state.collab_user}** (they may have seen everything predicted for them).")