import argparse
from . import soundcloud
from .models import LikedTrack
from . import db
import re

link_regex = r"https?:\/\/.*\s"

def main():
    parser = argparse.ArgumentParser(description="SoundKlau: A SoundCloud download and track import tool")
    parser.add_argument("--user", type=int, help="The user ID of the SoundCloud account to download likes from")
    parser.add_argument("--client_id", type=str, help="The SoundCloud client ID to use for API requests. If not provided, one will be scraped from the website")
    parser.add_argument("--auth_token", type=str, help="OAuth token for Soundcloud. Grab it from your browser console if you want to use soundcloud-native downloads")
    args = parser.parse_args()

    if args.client_id is not None:
        soundcloud.set_client_id(args.client_id)
    if args.auth_token is not None:
        soundcloud.set_auth_token(args.auth_token)
    if args.user is not None:
        print(f"Fetching liked tracks for user {args.user}...")
        likes = soundcloud.fetch_liked_tracks(args.user)
        number_fetched = len(likes)
        print(f'Fetched {number_fetched} likes')
        db.store_liked_tracks(likes)

    
    tracks = db.get_all_stored_tracks()
    print(f"Found {len(tracks)} tracks")
    for track in tracks:
        url = None
        try:
            description_matches = re.findall(link_regex, track['description'])
            if track['downloadable']:
                filename = soundcloud.download_track(track['id'])
                url = f"Downloaded as {filename}"
            elif 'purchase_url' in track and track['purchase_url'] is not None:
                url = track['purchase_url']
                url = description_matches
            else:
                url = description_matches + [track['permalink_url']]
            print(f'{track["title"]}: {url}')
        except Exception as e:
            print(f"Error processing track {track['title']}: {e}")
            continue