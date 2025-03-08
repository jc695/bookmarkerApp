from pydantic import BaseModel
import readabilipy
import requests
import bleach

# Pydantic models for type safety
class ArticleResult(BaseModel):
    title: str
    content: str
    url: str

class ParseError(BaseModel):
    error: str

# HTML sanitization config
ALLOWED_TAGS = ['p', 'h1', 'h2', 'h3', 'br', 'hr', 'pre', 'code', 'blockquote']

def parse_article(url: str) -> ArticleResult | ParseError:
    """Parse article content with error handling"""
    try:
        if not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL format")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        article = readabilipy.simple_json_from_html_string(response.text)
        
        # Handle complex plain_text structures
        plain_text = article.get('plain_text', '')
        if isinstance(plain_text, list):
            processed = []
            for item in plain_text:
                if isinstance(item, dict):
                    # Extract text from dictionary elements
                    processed.append(item.get('text', ''))
                else:
                    processed.append(str(item))
            plain_text = ' '.join(processed)
        
        clean_content = bleach.clean(
            plain_text,
            tags=ALLOWED_TAGS,
            strip=True
        )
        
        return ArticleResult(
            title=article.get('title', url),
            content=clean_content,
            url=url
        )
        
    except Exception as e:
        return ParseError(error=str(e))