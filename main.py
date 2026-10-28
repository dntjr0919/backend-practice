import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Guestbook(Base):
    __tablename__ = "guestbook"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

app = FastAPI()

# 프론트엔드 통신 허용 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 배포 후에는 Vercel 도메인으로 한정 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class EntryCreate(BaseModel):
    name: str
    message: str

@app.get("/api/guestbook")
def read_entries(db: Session = Depends(get_db)):
    return db.query(Guestbook).order_by(Guestbook.created_at.desc()).all()

@app.post("/api/guestbook")
def create_entry(entry: EntryCreate, db: Session = Depends(get_db)):
    db_item = Guestbook(name=entry.name, message=entry.message)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item