from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

app = FastAPI()
templates = Jinja2Templates(directory="frontend/templates")  # Create a templates directory

class Bookmark(BaseModel):
    id: Optional[str] = None
    title: str
    url: str
    description: Optional[str] = None
    folder: Optional[str] = None
    keywords: Optional[List[str]] = None

# In-memory datastore
bookmarks_db = {}

@app.get("/bookmarks", response_class=HTMLResponse)
async def get_bookmarks():
    # Render bookmarks as HTML snippets (using Jinja2)
    return templates.TemplateResponse("bookmarks.html", {"request": {}, "bookmarks": list(bookmarks_db.values())})

@app.get("/folders", response_class=HTMLResponse)
async def get_folders():
    folders = {b.folder for b in bookmarks_db.values() if b.folder}
    return templates.TemplateResponse("folders.html", {"request": {}, "folders": list(folders)})

@app.get("/bookmark-form", response_class=HTMLResponse)
async def get_bookmark_form():
    return templates.TemplateResponse("bookmark_form.html", {"request": {}})

@app.post("/api/bookmarks", response_model=Bookmark)
async def create_bookmark(bookmark: Bookmark):
    bookmark.id = str(uuid4())
    bookmarks_db[bookmark.id] = bookmark
    return bookmark
