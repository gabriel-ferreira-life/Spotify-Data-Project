
# Music Recommendation System

This project is a personalized music recommendation system that integrates machine learning models with the Spotify API to provide tailored music recommendations and playlist management. Built as a user-friendly web application using Streamlit, the system allows users to discover new music and organize playlists seamlessly.

---

## Features

- **Integration with Spotify API**  
  Users can log in with their Spotify accounts to access personalized recommendations and manage playlists directly in their library.

- **Tailored Music Recommendations**  
  Generate song suggestions based on moods or similarity to user-selected tracks using pre-trained machine learning models.

- **Playlist Management**  
  Create or update Spotify playlists with recommended songs in just a few clicks.

- **Interactive Web Application**  
  Built using Streamlit for a clean and intuitive user interface.

- **Secure Authentication**  
  Utilizes Spotipy and OAuth2 for secure user authentication and token management.

- **Scalable Deployment**  
  Hosted on Streamlit Cloud for easy accessibility and reliable performance.

---

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.11
- Spotify Developer Account (to generate API credentials)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gabriel-ferreira-life/Spotify-Data-Project.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Spotify Developer credentials:
   - Create an app on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Add your **Client ID**, **Client Secret**, and **Redirect URI** to a `.env` file:
     ```
     SPOTIPY_CLIENT_ID=your_client_id
     SPOTIPY_CLIENT_SECRET=your_client_secret
     SPOTIPY_REDIRECT_URI=your_redirect_uri
     ```

---

## Usage

1. **Run the Application**  
   Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. **Authenticate with Spotify**  
   - Log in with your Spotify account when prompted.
   - Authorize the app to access your Spotify data.

3. **Discover Music**  
   - Choose a recommendation method: similarity-based or mood-based.
   - Explore suggested tracks and create playlists in your Spotify library.

---

## Technologies Used

- **Programming Language**: Python
- **Framework**: Streamlit
- **API Client**: Spotipy
- **Machine for Recommendation**: Pre-trained clustering and similarity models
- **Deployment**: Streamlit Cloud

---

## Full Report

For a detailed breakdown of this project, please refer to the full report in the [PDF](report/Barros and Ferreira - Final Report.pdf).