import pytest
import requests
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from bookmarker.main import app, articles_db
from bookmarker.parser import parse_article, ArticleResult, ParseError
from pytest_httpserver import HTTPServer

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    articles_db.clear()

@pytest.fixture
def sample_html():
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Title</h1>
            <p>First paragraph</p>
            <p>Second paragraph</p>
        </body>
    </html>
    """

def test_save_article_flow():
    with patch("bookmarker.main.parse_article") as mock_parse:
        mock_parse.return_value = ArticleResult(
            title="Test Article",
            content="Test Content",
            url="http://test.url"
        )
        
        response = client.post("/save", 
                             data={"url": "http://test.url"},
                             follow_redirects=False)
        assert response.status_code == 303
        
        response = client.get("/dashboard")
        assert "Test Article" in response.text
        assert 'href="http://test.url"' in response.text

        article_id = next(iter(articles_db.keys()))
        response = client.get(f"/article/{article_id}")
        assert "Test Content" in response.text

        response = client.delete(f"/article/{article_id}")
        assert response.status_code == 204
        assert article_id not in articles_db

def test_save_article_htmx():
    with patch("bookmarker.main.parse_article") as mock_parse:
        mock_parse.return_value = ArticleResult(
            title="HTMX Article",
            content="HTMX Content",
            url="http://htmx.url"
        )
        
        response = client.post("/save",
                             data={"url": "http://htmx.url"},
                             headers={"hx-request": "true"})
        assert response.status_code == 200
        assert "HTMX Article" in response.text
        assert 'href="http://htmx.url"' in response.text

def test_save_article_error():
    with patch("bookmarker.main.parse_article") as mock_parse:
        mock_parse.return_value = ParseError(error="Invalid URL")
        
        response = client.post("/save", data={"url": "http://error.url"})
        assert response.status_code == 400
        assert "Invalid URL" in response.text.replace("&quot;", '"')

@patch("bookmarker.parser.requests.get")
@patch("bookmarker.parser.readabilipy.simple_json_from_html_string")
def test_full_integration(mock_readability, mock_get):
    mock_get.return_value = Mock(text="<html>content</html>")
    mock_readability.return_value = {
        "title": "Integration Test",
        "plain_text": "<p>Integration Content</p>"
    }
    
    response = client.post("/save", data={"url": "http://integration.url"})
    assert response.status_code in [200, 303]
    
    response = client.get("/dashboard")
    assert "Integration Test" in response.text
    assert 'href="http://integration.url"' in response.text
    
    article_id = next(iter(articles_db.keys()))
    response = client.get(f"/article/{article_id}")
    assert "Integration Content" in response.text
    
    response = client.delete(f"/article/{article_id}")
    assert response.status_code == 204

def test_real_html_parsing(httpserver: HTTPServer, sample_html):
    httpserver.expect_request("/test").respond_with_data(sample_html)
    url = httpserver.url_for("/test")
    
    result = parse_article(url)
    
    assert isinstance(result, ArticleResult)
    assert result.title == "Test Page"
    assert "Main Title" in result.content
    assert "First paragraph" in result.content

def test_invalid_url_format():
    result = parse_article("invalid-url")
    assert isinstance(result, ParseError)
    assert "Invalid URL format" in result.error

def test_http_error(httpserver: HTTPServer):
    httpserver.expect_request("/404").respond_with_data(status=404)
    url = httpserver.url_for("/404")
    
    result = parse_article(url)
    assert isinstance(result, ParseError)
    assert "404 Client Error" in result.error

@patch("bookmarker.parser.requests.get")
def test_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.ReadTimeout("Read timed out")
    
    result = parse_article("http://timeout.url")
    
    assert isinstance(result, ParseError)
    assert "Read timed out" in result.error

def test_complex_content_parsing(httpserver: HTTPServer):
    complex_html = """
    <html>
        <head><title>Complex Test</title></head>
        <body>
            <h1>List Test</h1>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <script>alert('xss')</script>
        </body>
    </html>
    """
    httpserver.expect_request("/complex").respond_with_data(complex_html)
    url = httpserver.url_for("/complex")
    
    result = parse_article(url)
    
    assert isinstance(result, ArticleResult)
    assert "List Test" in result.content
    assert "Item 1" in result.content
    assert "Item 2" in result.content
    assert "script" not in result.content.lower()