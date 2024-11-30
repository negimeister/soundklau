import argparse
from . import soundcloud
from .models import LikedTrack
from . import db
import re
from . import utils
import ffmpeg
import os
from mutagen.flac import FLAC


link_regex = r"https?:\/\/.*\s"

def download_track(track):
    url = None
    description_matches = re.findall(link_regex, track.description)
    utils.print_song_details(track.title, track.username, track.permalink_url)
    if track.downloadable:
        print("Track has native download. Downloading it now...")
        folder = "downloads"
        filename = soundcloud.download_track(track.id, folder)
        print(f"Downloaded to {filename}")
        db.update_track_download_path(track.id, os.path.join(os.path.abspath(filename)))
        db.update_track_state(track.id, 'downloaded')
    else:
        if track.purchase_url is not None:
            print(f"Track has a purchase URL: {track.purchase_url}")
        else:
            print("Found the following links in the description:")
            utils.print_urls(description_matches)
        if(utils.prompt_yes_no("Did you find a download?")):
            path = input("Provide the path to the downloaded file or press Enter it later: ").strip("'")
            db.update_track_download_path(track.id, os.path.abspath(path))
            db.update_track_state(track.id, 'downloaded')
        else:
            db.update_track_state(track.id, 'not_downloadable')

def is_track_download_available(track):
    if track.download_path is None:
        return False
    return os.path.exists(track.download_path)

def convert_track(track):
    if(is_track_download_available(track)):
        if os.path.splitext(track.download_path)[1] == ".flac":
            db.update_track_state(track.id, 'converted')
            return
        old_name = track.download_path
        new_name = os.path.splitext(track.download_path)[0] + ".flac"
        print(f"Converting track {track.title}")
        try:
            ffmpeg.input(track.download_path).output(new_name, map_metadata="0", loglevel="quiet").run()
        except Exception as e:
            print(f"Error converting track {track.title}: {e}")
            db.update_track_state(track.id, 'conversion_error')
            return
        db.update_track_download_path(track.id, new_name)
        db.update_track_state(track.id, 'converted')
        os.remove(old_name)
    else:
        print(f"Track {track.title} is not downloaded yet or the file is missing.")
        if(utils.prompt_yes_no("Do you want to download it now?")):
            download_track(track)
            track = db.find_track_by_id(track.id)
            convert_track(track)


def tag_track(track):
    if not is_track_download_available(track):
        print(f"Track {track.title} is not downloaded yet or the file is missing.")
        if(utils.prompt_yes_no("Do you want to download it now?")):
            download_track(track)
            track = db.find_track_by_id(track.id)
            convert_track(track)
        else:
            return

    utils.print_song_details(track.title, track.username, track.permalink_url)
    flac = FLAC(track.download_path)
    artist = flac.get('artist', [""])[0]
    title = flac.get('title', [""])[0]
    if artist:
        print(f"Artist: {artist}")
    else:
        artist = input("Artist: ")
        flac['artist'] = artist
    if title:
        print(f"Title: {title}")
    else:
        title = input("Title: ")
        flac['title'] = title
    flac.save()
    db.update_track_state(track.id, 'tagged')


def main():
    parser = argparse.ArgumentParser(description="SoundKlau: A SoundCloud download and track import tool")
    parser.add_argument("--user", type=int, help="The user ID of the SoundCloud account to download likes from")
    parser.add_argument("--client_id", type=str, help="The SoundCloud client ID to use for API requests. If not provided, one will be scraped from the website")
    parser.add_argument("--auth_token", type=str, help="OAuth token for Soundcloud. Grab it from your browser console if you want to use soundcloud-native downloads")
    parser.add_argument("--db", type=str, default="sqlite:///soundklau.db", help="Path of the sqlite DB")
    args = parser.parse_args()
    
    db.setup_db(args.db)

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

    
    tracks = db.find_tracks_by_state('new')
    print(f"Found {len(tracks)} new tracks")
    for track in tracks:
        download_track(track)
    
    tracks = db.find_tracks_by_state('downloaded')
    for track in tracks:
        convert_track(track)
    
    tracks = db.find_tracks_by_state('converted')
    for track in tracks:
        tag_track(track)