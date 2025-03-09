from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from bookmarker.parser import parse_article, ArticleResult, ParseError

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")
templates = Jinja2Templates(directory="src/frontend/templates")

articles_db = {}

@app.get("/")
async def home(request: Request):
    return RedirectResponse("/dashboard", status_code=303)

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {"request": request, "articles": articles_db.values()}
    )

@app.post("/save")
async def save_article(request: Request, url: str = Form(...)):
    parsed = parse_article(url)
    
    if isinstance(parsed, ParseError):
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": parsed.error},
            status_code=400
        )

    article_id = str(uuid4())
    articles_db[article_id] = {**parsed.model_dump(), "id": article_id}

    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(
            "partials/article_card.html",
            {"request": request, "article": articles_db[article_id]}
        )
    
    return RedirectResponse("/dashboard", status_code=303)

@app.get("/article/{article_id}")
async def view_article(request: Request, article_id: str):
    article = articles_db.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return templates.TemplateResponse(
        "pages/article.html",
        {"request": request, "article": article}
    )

@app.delete("/article/{article_id}")
async def delete_article(article_id: str):
    if article_id in articles_db:
        del articles_db[article_id]
    return HTMLResponse(status_code=204)