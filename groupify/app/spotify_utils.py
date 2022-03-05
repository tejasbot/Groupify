import pandas as pd
import numpy as np


def get_user_top_tracks(sp):
    '''
    Given user auth, get a combination of users top tracks and recently played music 
    '''

    results_top_tracks = sp.current_user_top_tracks(limit=25, offset=0,time_range='medium_term')
    results_recently_played = sp.current_user_recently_played(limit=25)
    all_results = {}
    all_results['items'] = results_top_tracks['items']
    print(type(all_results['items']))
    for ind, item in enumerate(results_recently_played['items']): 
        all_results['items'] = all_results['items'] + [results_recently_played['items'][ind]['track']]

    # all_results['items'] += results_try['items']
    results = all_results

    track_name = []
    track_id = []
    artist = []
    artist_id = []
    album = []
    duration = []
    popularity = []
    
    for i, items in enumerate(results['items']):
        track_name.append(items['name'])
        track_id.append(items['id'])
        artist.append(items["artists"][0]["name"])
        artist_id.append(items["artists"][0]["id"])
        duration.append(items["duration_ms"])
        album.append(items["album"]["name"])
        popularity.append(items["popularity"])
        
    df_favorite = pd.DataFrame({ "track_name": track_name, 
    "album": album,
    "track_id": track_id,
    "artist": artist,
    "artist_id": artist_id,
    "duration": duration,
    "popularity": popularity})
    return df_favorite


def fetch_audio_features(sp, df):
    playlist = df[['track_id','track_name', 'artist_id']] 
    index = 0
    audio_features = []
    genres = []
    
    # Make the API request
    while index < playlist.shape[0]:
        audio_features += sp.audio_features(playlist.iloc[index:index + 50, 0])
        index += 50
        
    index = 0
    #while index < playlist.shape[0]:
     #   genres += [sp.artist('spotify:artist:'+ playlist.iloc[index, 2])['genres']]
      #  index += 1
    
    # Create an empty list to feed in different charactieritcs of the tracks
    features_list = []
    #Create keys-values of empty lists inside nested dictionary for album
    for features in audio_features:
        features_list.append([features['danceability'],
        features['acousticness'],
        features['energy'],
        features['tempo'],
        features['instrumentalness'],
        features['loudness'],
        features['liveness'],
        features['duration_ms'],
        features['key'],
        features['valence'],
        features['speechiness'],
        features['mode']])
    

    
    df_audio_features = pd.DataFrame(features_list, columns=['danceability', 'acousticness', 'energy','tempo',
    'instrumentalness', 'loudness', 'liveness','duration_ms', 'key',
    'valence', 'speechiness', 'mode',])
    
    #df_audio_features['genres'] = genres
    df_audio_features['track_id'] = playlist['track_id'].values
    # Create the final df, using the 'track_id' as index for future reference
    #df_playlist_audio_features = pd.concat([playlist, df_audio_features], axis=0)
    #df_playlist_audio_features.set_index('track_name', inplace=True, drop=True)
    df_audio_features.set_index('track_id', inplace=True, drop=True)
    return df_audio_features#df_playlist_audio_features



def mean_of_song_features(songs_of_all_users):
    return pd.DataFrame(songs_of_all_users.median(), columns= ['fav_playlist'])

def normalize_songs_with_common_user_features(songs_of_all_users, mean_of_song_features):
    new_dataframe=songs_of_all_users.subtract(mean_of_song_features.squeeze(), axis=1)
    new_dataframe.divide(mean_of_song_features, axis='columns')
    new_dataframe.drop(['instrumentalness'], axis=1)
    new_dataframe['variation'] = new_dataframe.sum(axis=1)
    new_dataframe['variation'] = new_dataframe['variation'].abs()
    new_dataframe = new_dataframe.drop_duplicates()
    new_dataframe=new_dataframe.nsmallest(50,'variation', keep='first')
    
    return new_dataframe.index

def create_playlist_new(sp, playlist_name = "TestPlaylist", playlist_description="Test Playlist"):
    user =  sp.current_user()['id']
    playlists = sp.user_playlist_create(user,playlist_name, description = playlist_description)
    playlist_id = playlists['id']
    return playlist_id


def enrich_playlist(sp, username, playlist_id, playlist_tracks):
    index = 0
    results = []
    
    while index < len(playlist_tracks):
        results += sp.user_playlist_add_tracks(username, playlist_id, tracks = playlist_tracks[index:index + 50])
        index += 50