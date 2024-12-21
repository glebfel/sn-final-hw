from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib

DATABASE_URL = "sqlite:///./shorturl.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


class ShortURL(Base):
    __tablename__ = "shorturls"
    id = Column(Integer, primary_key=True, index=True)
    short_id = Column(String, unique=True, index=True)
    full_url = Column(String)


Base.metadata.create_all(bind=engine)


class URLCreate(BaseModel):
    url: str


@app.post("/shorten")
def shorten_url(payload: URLCreate):
    db = SessionLocal()
    short_id = hashlib.md5(payload.url.encode()).hexdigest()[:8]
    short_url = ShortURL(short_id=short_id, full_url=payload.url)
    db.add(short_url)
    db.commit()
    db.refresh(short_url)
    db.close()
    return {"short_id": short_url.short_id, "short_url": f"http://localhost:8001/{short_id}"}


@app.get("/{short_id}")
def redirect_url(short_id: str):
    db = SessionLocal()
    url = db.query(ShortURL).filter(ShortURL.short_id == short_id).first()
    db.close()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"full_url": url.full_url}


@app.get("/stats/{short_id}")
def url_stats(short_id: str):
    db = SessionLocal()
    url = db.query(ShortURL).filter(ShortURL.short_id == short_id).first()
    db.close()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"short_id": url.short_id, "full_url": url.full_url}
