import streamlit as st
import pickle
import random

st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #000000;
    }
    
    /* Force all text to be neon green and monospace */
    h1, h2, h3, p, label, div, span, li {
        color: #00FF00 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* Style buttons like terminal commands */
    .stButton>button {
        background-color: #000000 !important;
        color: #00FF00 !important;
        border: 2px solid #00FF00 !important;
        border-radius: 0px !important;
        font-weight: bold;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: #00FF00 !important;
        color: #000000 !important;
    }
    
    /* Style the dropdown boxes */
    div[data-baseweb="select"] > div {
        background-color: #000000 !important;
        border: 1px solid #00FF00 !important;
        border-radius: 0px !important;
        color: #00FF00 !important;
    }
    
    /* Style the dropdown list items */
    ul[data-baseweb="menu"] {
        background-color: #000000 !important;
        border: 1px solid #00FF00 !important;
    }
    li[data-baseweb="menu-item"] {
        color: #00FF00 !important;
    }
    
    /* Make dividers look like dashed terminal lines */
    hr {
        border-top: 1px dashed #00FF00 !important;
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

st.text("""
===================================================
  __  __            _        ____                
 |  \/  | _____   _(_) ___  |  _ \ ___  ___ ___  
 | |\/| |/ _ \ \ / / |/ _ \ | |_) / _ \/ __/ __| 
 | |  | | (_) \ V /| |  __/ |  _ <  __/ (__\__ \ 
 |_|  |_|\___/ \_/ |_|\___| |_| \_\___|\___|___/ 
                                                 
   R E C O M M E N D A T I O N   E N G I N E     
===================================================
""")

st.header("> CONTENT_BASED.EXE")
st.write("Find similar movies based on genre and metadata.")

selected_movie = st.selectbox("Search for a movie you personally like:", movie_titles)

if st.button("RUN CONTENT_SEARCH"):
    st.session_state.content_results = content_recs.get(selected_movie, [])
    st.session_state.content_movie = selected_movie

if st.session_state.content_results:
    st.write(f"Because you liked **{st.session_state.content_movie}**, based on the model we recommend:")
    for title in st.session_state.content_results:
        st.write(f"  [+] {title}")

st.divider()

st.header("> COLLAB_FILTER.EXE")
st.write("Discover different movies based on other user's favorite movies.")

def pick_random_user():
    st.session_state.user_dropdown = random.choice(valid_users)

selected_user = st.selectbox("Select a User ID:", valid_users, key="user_dropdown")

col1, col2 = st.columns(2)

with col1:
    if st.button("RUN COLLAB_SEARCH"):
        user_predictions = predictions_df.loc[selected_user].sort_values(ascending=False)
        seen_movies = user_history.get(selected_user, [])
        st.session_state.collab_results = user_predictions.drop(seen_movies, errors='ignore').head(5).index.tolist()
        st.session_state.collab_user = selected_user

with col2:
    st.button("RANDOM USER ID", on_click=pick_random_user)

if st.session_state.collab_results:
    st.write(f"Recommendations from User **{st.session_state.collab_user}**:")
    for title in st.session_state.collab_results:
        st.write(f"  [+] {title}")