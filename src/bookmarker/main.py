from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from bookmarker.parser import parse_article, ArticleResult, ParseError

app = FastAPI()
templates = Jinja2Templates(directory="src/frontend/templates")

articles_db = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return RedirectResponse("/dashboard", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"request": request, "articles": articles_db.values()}
    )

@app.post("/save", response_class=HTMLResponse)
async def save_article(request: Request, url: str = Form(...)):
    parsed = parse_article(url)
    
    if isinstance(parsed, ParseError):
        return templates.TemplateResponse(
            request,
            "error.html",
            {"request": request, "error": parsed.error},
            status_code=400
        )

    article_id = str(uuid4())
    articles_db[article_id] = {**parsed.model_dump(), "id": article_id}

    # Exact header check for HTMX requests
    if request.headers.get("hx-request") == "true":
        return templates.TemplateResponse(
            request,
            "partials/article_card.html",
            {"request": request, "article": articles_db[article_id]}
        )
    return RedirectResponse("/dashboard", status_code=303)

@app.get("/article/{article_id}", response_class=HTMLResponse)
async def view_article(request: Request, article_id: str):
    article = articles_db.get(article_id)
    if not article:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse(
        request,
        "article.html",
        {"request": request, "article": article}
    )

@app.delete("/article/{article_id}", response_class=HTMLResponse)
async def delete_article(article_id: str):
    if article_id in articles_db:
        del articles_db[article_id]
    return HTMLResponse(status_code=204)