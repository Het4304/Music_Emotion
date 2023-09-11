import streamlit as st
import cv2
import requests
from fer import FER
import base64

# Constants
SPOTIPY_CLIENT_ID = 'YOUR SPOTIFY CLIENT ID '
SPOTIPY_CLIENT_SECRET = 'YOUR SPOTIFY CLIENT SECRET'
EMOTION_LABELS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

# Initialize Spotify API client
client_credentials = f"{SPOTIPY_CLIENT_ID}:{SPOTIPY_CLIENT_SECRET}"
client_credentials_base64 = base64.b64encode(client_credentials.encode())
token_url = 'https://accounts.spotify.com/api/token'
headers = {
    'Authorization': f'Basic {client_credentials_base64.decode()}'
}
data = {
    'grant_type': 'client_credentials'
}
response = requests.post(token_url, data=data, headers=headers)
if response.status_code == 200:
    access_token = response.json()['access_token']
    print("sads",access_token)
headers1 = {
    'Authorization': f'Bearer {access_token}'  # Replace with your actual access token
}
emotion_to_attributes = {
    'angry': {'attribute': 'angry', 'min_val': 0.7, 'max_val': 1.0},
    'disgust': {'attribute': 'disgust', 'min_val': 0.7, 'max_val': 1.0},
    'fear': {'attribute': 'fear', 'min_val': 0.7, 'max_val': 1.0},
    'happy': {'attribute': 'happy', 'min_val': 0.7, 'max_val': 1.0},
    'sad': {'attribute': 'sad', 'min_val': 0.0, 'max_val': 0.3},
    'surprise': {'attribute': 'surprise', 'min_val': 0.7, 'max_val': 1.0},
    'neutral': {'attribute': 'neutral', 'min_val': 0.0, 'max_val': 1.0}
}
# Load face detection cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# Initialize emotion predictor from fer module
emotion_predictor = FER()


def main():
    st.title("Emotion-based Song Recommendation")
    cap = cv2.VideoCapture(0)
    stframe = st.empty()
    samples_taken = 0
    detected_emotions = []
    while samples_taken < 2:
        ret, frame = cap.read()
        if not ret:
            break
        # Detect faces in the frame
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        emotions = emotion_predictor.detect_emotions(frame)
        for (x, y, w, h) in faces:
            # Detect emotion from the face
            if emotions:
                detected_emotion = max(emotions[0]['emotions'], key=emotions[0]['emotions'].get)
                detected_emotions.append(detected_emotion)
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Display detected emotion text
                cv2.putText(frame, detected_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        stframe.image(frame, channels="BGR", use_column_width=True)
        samples_taken += 1
    cap.release()
    if detected_emotions:
        last_detected_emotion = detected_emotions[-1].lower()  # Convert to lowercase
        print("Last detected emotion:", last_detected_emotion)  # Print the detected emotion
        if last_detected_emotion in emotion_to_attributes:
            recommended_tracks = get_recommendations_for_emotions(last_detected_emotion)
            display_recommendations(recommended_tracks)
        else:
            print("Emotion not found in emotion_to_attributes:", last_detected_emotion)


# Function to get song recommendations based on emotion attribute
def get_recommendations(attribute):
    recommended_tracks = []
    music_id = get_seed_track_id(attribute)
    playlist_url = f'https://api.spotify.com/v1/playlists/{music_id[0]}/tracks'
    response1 = requests.get(playlist_url, headers=headers1)
    if response1.status_code == 200:
        data1 = response1.json()
        tracks = data1.get('items', [])
        for track in tracks:
            track_info = track['track']
            print("Track Name:", track_info['name'])
            print("Artist(s):", ', '.join([artist['name'] for artist in track_info['artists']]))
            print("Album:", track_info['album']['name'])
            print()
            track_info2 = {
                'name': track_info['name'],
                'artists': [artist['name'] for artist in track_info['artists']]
            }
            recommended_tracks.append(track_info2)
    else:
        print("Error:", response.status_code)
    return recommended_tracks


# Function to get song recommendations based on emotion and attribute
def get_recommendations_for_emotions(detected_emotions):
    recommended_tracks = []
    detected_emotion = detected_emotions
    if detected_emotion in emotion_to_attributes:
        emotion_class = emotion_to_attributes[detected_emotion]['attribute']
        recommended_tracks.extend(get_recommendations(emotion_class))
        return recommended_tracks


def get_seed_track_id(attribute):
    if attribute == 'sad':
        return ['7zNvXEjgmE1110slXAuZie']
    elif attribute == 'happy':
        return ['37i9dQZF1DWYRTlrhMB12D']
    elif attribute == 'neutral':
        return ['37i9dQZF1DWYRTlrhMB12D']
    elif attribute == 'angry':
        return ['2KAl1ayr9hJLXbic137j4W']
    else:
        return []


# Function to display song recommendations


def display_recommendations(recommended_tracks):
    st.write(f"Recommended Songs:")
    for track in recommended_tracks:
        st.write(f"- {track['name']} by {', '.join(track['artists'])}")


if __name__ == "__main__":
    main()
