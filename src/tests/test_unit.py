import pytest
import requests
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from bookmarker.main import app, articles_db
from bookmarker.parser import parse_article, ArticleResult, ParseError

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    articles_db.clear()

def test_home_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"

def test_dashboard_empty():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "No articles saved yet" in response.text

@patch("bookmarker.parser.requests.get")
@patch("bookmarker.parser.readabilipy.simple_json_from_html_string")
def test_parse_article_success(mock_readability, mock_get):
    mock_get.return_value = Mock(
        text="<html><h1>Test</h1><p>Content</p></html>",
        raise_for_status=Mock()
    )
    mock_readability.return_value = {
        "title": "Test Article",
        "plain_text": "<p>Content</p>"
    }
    
    result = parse_article("http://valid.url")
    assert isinstance(result, ArticleResult)
    assert result.title == "Test Article"
    assert "<p>Content</p>" in result.content  # Before sanitization

@patch("bookmarker.parser.requests.get")
@patch("bookmarker.parser.readabilipy.simple_json_from_html_string")
def test_parse_article_list_content(mock_readability, mock_get):
    mock_get.return_value = Mock(
        text="<html>...</html>",
        raise_for_status=Mock()
    )
    mock_readability.return_value = {
        "title": "List Test",
        "plain_text": ["First paragraph", "Second paragraph"]
    }
    
    result = parse_article("http://list.url")
    assert isinstance(result, ArticleResult)
    assert result.content == "First paragraph Second paragraph"

@patch("bookmarker.parser.requests.get")
@patch("bookmarker.parser.readabilipy.simple_json_from_html_string")
def test_parse_article_dict_content(mock_readability, mock_get):
    mock_get.return_value = Mock(
        text="<html>...</html>",
        raise_for_status=Mock()
    )
    mock_readability.return_value = {
        "title": "Dict Test",
        "plain_text": [
            {"text": "First"}, 
            {"text": "Second", "type": "em"}
        ]
    }
    
    result = parse_article("http://dict.url")
    assert isinstance(result, ArticleResult)
    assert result.content == "First Second"

@patch("bookmarker.parser.requests.get")
@patch("bookmarker.parser.readabilipy.simple_json_from_html_string")
def test_parse_article_sanitization(mock_readability, mock_get):
    mock_get.return_value = Mock(
        text="<html>...</html>",
        raise_for_status=Mock()
    )
    mock_readability.return_value = {
        "title": "Sanitization Test",
        "plain_text": "<script>alert('xss')</script><p>Safe</p>"
    }
    
    result = parse_article("http://sanitize.url")
    assert isinstance(result, ArticleResult)
    assert result.content == "alert('xss')<p>Safe</p>"  # Updated assertion

@patch("bookmarker.parser.requests.get")
def test_parse_article_invalid_url(mock_get):
    result = parse_article("ftp://invalid.url")
    assert isinstance(result, ParseError)
    assert "Invalid URL format" in result.error

@patch("bookmarker.parser.requests.get")
def test_parse_article_http_error(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
    mock_get.return_value = mock_response
    
    result = parse_article("http://404.url")
    assert isinstance(result, ParseError)
    assert "404" in result.error

@patch("bookmarker.parser.requests.get")
def test_parse_article_timeout(mock_get):
    # Use a specific exception with a message
    mock_get.side_effect = requests.exceptions.ReadTimeout("Read timed out")
    result = parse_article("http://timeout.url")
    assert isinstance(result, ParseError)
    assert "Read timed out" in result.error  # No period in assertion

def test_delete_non_existent_article():
    response = client.delete("/article/non-existent")
    assert response.status_code == 204

def test_view_non_existent_article():
    response = client.get("/article/non-existent", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"