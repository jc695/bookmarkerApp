Here's a professional README.md template for your project:

```markdown
# Bookmarker API

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

A web-based article bookmarking service that saves, parses, and displays article content with a clean interface.

## Features

- Save articles via URL input
- Automatic content extraction using Readability.js
- Clean HTML sanitization for security
- HTMX-powered dynamic UI updates
- Dockerized deployment
- RESTful API endpoints
- Error handling and validation
- Responsive web interface

## Project Structure

```text
.
├── src
│   ├── bookmarker           # FastAPI application
│   │   ├── main.py          # API routes and HTMX handlers
│   │   └── parser.py        # Article parsing logic
│   ├── frontend             # HTML templates
│   └── tests                # Unit and integration tests
├── docker-compose.yml       # Container orchestration
└── Dockerfile               # Production build configuration
```

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)
- [uv](https://github.com/astral-sh/uv) (optional, for dependency management)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/bookmarker.git
cd bookmarker

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
uv sync  # or pip install -r requirements.txt
```

### Running Locally

```bash
# Development server with auto-reload
uvicorn src.bookmarker.main:app --reload

# Access at http://localhost:8000
```

### Docker Deployment

```bash
# Build and start containers
docker-compose up -d --build

# Access at http://localhost:8000
```

## Usage

### Save an Article
```bash
curl -X POST "http://localhost:8000/save" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "url=https://example.com/article"
```

### API Endpoints
| Method | Path             | Description                  |
|--------|------------------|------------------------------|
| POST   | /save            | Save new article             |
| GET    | /dashboard       | View saved articles          |
| GET    | /article/{id}    | View article content         |
| DELETE | /article/{id}    | Remove article               |

## Testing

```bash
# Run unit tests
pytest src/tests/test_unit.py -v

# Run integration tests
pytest src/tests/test_integration.py -v

# Full test suite
pytest -v
```

## Frontend
The interface uses:
- HTMX for dynamic content loading
- Bootstrap 5 for styling
- Jinja2 templating engine

Templates are located in `src/frontend/templates/`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Readabilipy](https://github.com/alan-turing-institute/readabilipy)
- [HTMX](https://htmx.org/)
- [Bleach](https://github.com/mozilla/bleach)
```

This template provides:
1. Clear project overview
2. Quickstart instructions
3. Detailed usage examples
4. Testing guidelines
5. Architecture explanation
6. Contribution guidelines
7. Technology acknowledgments

You can customize it further by adding:
- Screenshots of the UI
- API documentation link
- Example use cases
- Performance benchmarks
- Security considerations
- Version history