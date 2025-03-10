from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl
import httpx
from lxml import html
from urllib.parse import urljoin
import time
from typing import Optional

router = APIRouter()

class ResponseModel(BaseModel):
    title: str
    published_date: Optional[str] = None
    description: str
    thumbnail: HttpUrl
    source_url: HttpUrl
    site_name: Optional[str] = None  # Changed to optional
    process_ts: float

async def fetch_content(url: str) -> str:
    """Fetches webpage content."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
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
    
    def extract_site_name(self) -> Optional[str]:
        """Extracts site name from various meta tags with fallbacks."""
        # Try common site name meta tags
        site_name = (
            self.extract_attribute("site_name") or
            self.extract_attribute("site") or
            self.extract_attribute("application-name") or
            self.extract_attribute("publisher")  # Dublin Core or Open Graph
        )
        if site_name:
            return site_name

        # Try Twitter site (strip @ if present)
        twitter_site = self.extract_attribute("twitter:site")
        if twitter_site:
            return twitter_site.lstrip('@')

        # Fallback to parsing <title> tag
        title_tag = self.tree.xpath('//title/text()')
        if title_tag:
            title = title_tag[0].strip()
            # Assuming format like "Article Title - Site Name"
            parts = title.split(" - ")
            if len(parts) > 1:
                return parts[-1]  # Take the last part as site name

        # Final fallback: domain name from URL
        from urllib.parse import urlparse
        return urlparse(self.url).hostname

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

@router.get("/parse-webpage/", response_model=ResponseModel)
async def parse_webpage(url: str = Query(..., title="webpage URL")):
    start_time = time.perf_counter()

    try:
        html_content = await fetch_content(url)
        tree = html.fromstring(html_content)

        extractor = ContentExtractor(tree, url)

        title = extractor.extract_title()
        published_date = extractor.extract_published_date()
        description = extractor.extract_description()
        first_image = extractor.extract_first_image()
        source_url = urljoin(url, "/")
        site_name = extractor.extract_site_name()

        process_time = time.perf_counter() - start_time

        return ResponseModel(
            title=title,
            published_date=published_date,
            description=description,
            thumbnail=first_image,
            source_url=source_url,
            site_name=site_name,
            process_ts=process_time
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Failed to fetch web content")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))