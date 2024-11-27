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
                description=track.get('description', None),
                state='new',
                liked_at=like['created_at']
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
        
        
        return tracks
    
    except Exception as e:
        print(f"Error retrieving tracks: {e}")
        return []
    
    finally:
        session.close()

def update_track_state(track_id, new_state):
    session = SessionLocal()
    
    try:
        # Query the record from the LikedTrack table
        track = session.query(LikedTrack).filter_by(id=track_id).first()
        
        # Update the state of the track
        if track:
            track.state = new_state
            session.commit()
        else:
            print(f"Track {track_id} not found")
    
    except Exception as e:
        print(f"Error updating track state: {e}")
    
    finally:
        session.close()

def find_tracks_by_state(state):
    session = SessionLocal()
    
    try:
        # Query all records from the LikedTrack table with the specified state
        tracks = session.query(LikedTrack).filter_by(state=state).all()
        return tracks
    
    except Exception as e:
        print(f"Error finding tracks by state: {e}")
        return []
    finally:
        session.close()