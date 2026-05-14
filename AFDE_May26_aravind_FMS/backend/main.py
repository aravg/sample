from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import models
from database import engine, get_db
from routers import feedback
import crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Feedback Management System",
    description="Centralized feedback collection and management platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback.router)


@app.get("/")
def root():
    return {"message": "Feedback Management System API", "version": "1.0.0", "docs": "/docs"}


@app.get("/search")
def search_feedback(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    program_name: Optional[str] = Query(None, description="Filter by program name"),
    db: Session = Depends(get_db),
):
    return crud.search_feedback(db, keyword=keyword, rating=rating, program_name=program_name)
