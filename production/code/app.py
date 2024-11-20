import streamlit as st
from recommendation_page import show_recommendation_page
from exploration_page import show_exploration_page

method = st.sidebar.selectbox("Recommend or Explore", ("Recommendation", "Exploration"))

if method == "Recommendation":
    show_recommendation_page()

elif method == "Exploration":
    show_exploration_page()