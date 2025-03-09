from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, HttpUrl
import httpx
from lxml import html
from urllib.parse import urljoin
import uvicorn
import webbrowser
import time
from typing import Optional

app = FastAPI()

class ResponseModel(BaseModel):
    title: str
    published_date: Optional[str] = None
    description: str
    thumbnail: HttpUrl
    source_url: HttpUrl
    process_ts: float

async def fetch_content(url: str) -> str:
    """Fetches webpage content."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
    return response.text

class ContentExtractor:
    """Extracts metadata from a webpage."""

    def __init__(self, tree: html.HtmlElement, url: str):
        self.tree = tree
        self.url = url

    def extract_attribute(self, attribute: str) -> Optional[str]:
        """Extracts an attribute from standard HTML tags or metadata properties."""
        # Check standard HTML tag
        element = self.tree.find(f'.//{attribute}')
        if element is not None and element.text:
            return element.text.strip()

        # Check metadata properties
        meta_properties = [
            f'dc:{attribute}',
            f'twitter:{attribute}',
            f'og:{attribute}',
            f'weibo:{attribute}',
        ]
        
        for meta_property in meta_properties:
            value = self.tree.xpath(f'//meta[@property="{meta_property}"]/@content')
            if value:
                return value[0].strip()
        
        return None

    def extract_title(self) -> str:
        return self.extract_attribute("title") or "No title found"

    def extract_published_date(self) -> Optional[str]:
        return self.extract_attribute("published_time") or self.extract_attribute("modified_time")

    def extract_description(self) -> str:
        return self.extract_attribute("description") or "No description found"

    def extract_first_image(self) -> str:
        """Extracts the first available image URL."""
        image_meta_properties = ["og:image", "twitter:image", "dc:image", "weibo:image"]
        for meta_property in image_meta_properties:
            image_url = self.tree.xpath(f'//meta[@property="{meta_property}"]/@content')
            if image_url:
                return urljoin(self.url, image_url[0].strip())

        img_src = self.tree.xpath('//img/@src')
        return urljoin(self.url, img_src[0].strip()) if img_src else "https://example.com/default-thumbnail.jpg"

@app.get("/parse-blog/", response_model=ResponseModel)
async def parse_blog(url: str = Query(..., title="Blog URL")):
    start_time = time.perf_counter()

    try:
        html_content = await fetch_content(url)
        tree = html.fromstring(html_content)

        extractor = ContentExtractor(tree, url)
        title = extractor.extract_title()
        published_date = extractor.extract_published_date()
        description = extractor.extract_description()
        first_image = extractor.extract_first_image()

        process_time = time.perf_counter() - start_time

        return ResponseModel(
            title=title,
            published_date=published_date,
            description=description,
            thumbnail=first_image,
            source_url=url,
            process_ts=process_time
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Failed to fetch blog content")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8002/docs")
    uvicorn.run("test:app", host="127.0.0.1", port=8002, reload=True)
