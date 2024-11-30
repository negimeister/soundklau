from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LikedTrack(Base):
    __tablename__ = 'liked_tracks'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    username = Column(String, nullable=False)
    permalink_url = Column(String, nullable=False)
    downloadable = Column(Boolean, nullable=False)
    purchase_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    state = Column(String, nullable=False)
    liked_at = Column(String, nullable=False)
    download_path = Column(String, nullable=True)