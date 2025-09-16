from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    link = Column(String, unique=True)
    content = Column(Text)
    summary = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    published = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Metadata(Base):
    __tablename__ = "metadata"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True)
    value = Column(String)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

DATABASE_URL = "sqlite:///./news.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
