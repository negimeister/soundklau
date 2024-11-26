from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from soundklau.models import LikedTrack

DATABASE_URL = "sqlite:///soundklau.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def store_liked_tracks(likes):
    session = SessionLocal()
    count = 0
    for like in likes:
        try:
            if not 'track' in like:
                continue
            track = like['track']
            track_id = track['id']
            existing_track = session.query(LikedTrack).filter_by(id=track_id).first()
            if existing_track:
                continue
            liked_track = LikedTrack(
                id=track['id'],
                title=track.get('title', ''),
                username=track['user'].get('username', ''),
                permalink_url=track.get('permalink_url', ''),
                downloadable=track.get('downloadable', False) and track.get('has_downloads_left', False),
                purchase_url=track.get('purchase_url', None),
                description=track.get('description', None)
            )
            session.add(liked_track)
            count+=1
        except Exception as e:
            print(f"Error storing track {like}\n{e}")
    session.commit()
    session.close()
    print(f"Stored {count} new tracks in DB")

def get_all_stored_tracks():
    session = SessionLocal()
    
    try:
        # Query all records from the LikedTrack table
        tracks = session.query(LikedTrack).all()
        
        # Convert the list of LikedTrack objects to a list of dictionaries for easier handling
        track_list = [
            {
                'id': track.id,
                'title': track.title,
                'username': track.username,
                'permalink_url': track.permalink_url,
                'downloadable': track.downloadable,
                'purchase_url': track.purchase_url,
                'description': track.description
            }
            for track in tracks
        ]
        
        return track_list
    
    except Exception as e:
        print(f"Error retrieving tracks: {e}")
        return []
    
    finally:
        session.close()
