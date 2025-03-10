from typing import Dict, Optional, Any
from uuid import uuid4
from contextlib import asynccontextmanager
import os
import logging
import traceback

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

try:
    from bookmarker import logger
    from bookmarker.parser import router as parser_router, parse_webpage
except ImportError as e:
    raise ImportError(f"Failed to import parser module: {str(e)}")

import ZODB, ZODB.FileStorage
import transaction
from persistent.mapping import PersistentMapping

# Initialize ZODB with directory check
STORAGE_DIR = ".storage"
STORAGE_FILE = os.path.join(STORAGE_DIR, "articles.fs")

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

try:
    storage = ZODB.FileStorage.FileStorage(STORAGE_FILE)
    db = ZODB.DB(storage)
except Exception as e:
    logger.error(f"Failed to initialize ZODB: {str(e)}")
    raise

# Initialize application
def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")
    app.include_router(parser_router, prefix="/parser", tags=["parser"])
    return app

app = create_app()
try:
    templates = Jinja2Templates(directory="src/frontend/templates")
except Exception as e:
    logger.error(f"Failed to initialize templates: {str(e)}")
    raise

@asynccontextmanager
async def get_db():
    try:
        conn = db.open()
        root = conn.root()
        if not hasattr(root, 'articles_db'):
            root.articles_db = PersistentMapping()
            transaction.commit()
        yield conn
        transaction.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}\n{traceback.format_exc()}")
        transaction.abort()
        raise
    finally:
        conn.close()

def get_article_by_url(conn, url: str) -> Optional[str]:
    try:
        articles_db = conn.root().articles_db
        return next((article_id for article_id, article_data in articles_db.items() 
                    if article_data.get("source_url") == url), None)
    except Exception as e:
        logger.error(f"Error in get_article_by_url: {str(e)}")
        raise

def upsert_article(conn, parsed: Any, url: str) -> str:
    try:
        articles_db = conn.root().articles_db
        article_id = get_article_by_url(conn, url) or str(uuid4())
        articles_db[article_id] = {**parsed.dict(), "source_url": url}
        conn.root().articles_db = articles_db
        return article_id
    except Exception as e:
        logger.error(f"Error in upsert_article: {str(e)}")
        raise

@app.get("/", response_class=RedirectResponse)
async def home():
    return RedirectResponse("/dashboard", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db_conn=Depends(get_db)):
    try:
        async with db_conn as conn:
            articles = [(article_id, data) for article_id, data in conn.root().articles_db.items()]
            return templates.TemplateResponse(
                "pages/dashboard.html",
                {"request": request, "articles": articles}
            )
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save", response_class=HTMLResponse)
async def save_article(request: Request, url: str = Form(...), db_conn=Depends(get_db)):
    try:
        async with db_conn as conn:
            logger.debug(f"Attempting to save article from URL: {url}")
            existing_article_id = get_article_by_url(conn, url)
            
            if existing_article_id and request.headers.get("hx-request") == "true":
                return templates.TemplateResponse(
                    "partials/popup_feedback.html",
                    {"request": request, "message": "Article already exists!"}
                )
            
            parsed = await parse_webpage(url=url)
            article_id = upsert_article(conn, parsed, url)
            article = conn.root().articles_db[article_id]
            
            if request.headers.get("hx-request") == "true":
                return templates.TemplateResponse(
                    "partials/article_card.html",
                    {"request": request, "article": article, "article_id": article_id}
                )
            return RedirectResponse("/dashboard", status_code=303)
    except Exception as e:
        error_msg = f"Failed to save article: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_msg},
            status_code=500
        )

@app.get("/article/{article_id}", response_class=HTMLResponse)
async def view_article(request: Request, article_id: str, db_conn=Depends(get_db)):
    try:
        async with db_conn as conn:
            articles_db = conn.root().articles_db
            article = articles_db.get(article_id)
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            return templates.TemplateResponse(
                "pages/article.html",
                {"request": request, "article": article}
            )
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"View article error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/article", response_model=Dict[str, dict])
async def get_all_articles(db_conn=Depends(get_db)):
    try:
        async with db_conn as conn:
            return dict(conn.root().articles_db)
    except Exception as e:
        logger.error(f"Get all articles error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/article/{article_id}", response_class=HTMLResponse)
async def delete_article(request: Request, article_id: str, db_conn=Depends(get_db)):
    try:
        async with db_conn as conn:
            articles_db = conn.root().articles_db
            if article_id not in articles_db:
                raise HTTPException(status_code=404, detail="Article not found")
            del articles_db[article_id]
            conn.root().articles_db = articles_db
            
            # TODO - Not able to get the delete popup to work
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Delete article error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))