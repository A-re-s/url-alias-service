# URL Alias Service

A FastAPI-based service for creating and managing URL aliases (URL shortener service).

## 🚀 Features

- Create short aliases for long URLs
- Redirect users from short URLs to original URLs
- RESTful API with OpenAPI documentation
- Database-backed storage using SQLAlchemy
- Docker support for easy deployment
- Comprehensive test coverage
- Pre-commit hooks for code quality

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy with AsyncPG/SQLite support
- **Python Version**: 3.12
- **Documentation**: OpenAPI (Swagger)
- **Testing**: pytest with async support
- **Code Quality**: 
  - Black (code formatting)
  - Pylint (code analysis)
  - Pre-commit hooks
  - isort (import sorting)

## 📋 Prerequisites

- Python 3.12+
- Docker (optional, for containerized deployment)
- Make (optional, for using Makefile commands)
- Configure environment variables in `.env`:
  ```env
  DB_NAME=postgres
  DB_USER=postgres
  DB_PASSWORD=postgres
  DB_HOST=db_host
  DB_PORT=5432

  SECRET_KEY=your_secret_key
  
  API_PORT=8000
  ```
## 🚀 Installation Methods

### 1. Local Development (requires venv and PostgreSQL)

This method requires a local PostgreSQL installation and Python virtual environment.

1. Install PostgreSQL and create a database
2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate    # Windows
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run the application:
```bash
make run
```

### 2. Container Deployment (requires PostgreSQL)

This method runs the application in a Docker container but requires an external PostgreSQL instance.

1. Install PostgreSQL and create a database
2. Build and run the container:
```bash
make docker-run 
make docker-run-detached #detached mode
```

### 3. Docker Compose (fully containerized)

This is the recommended method as it sets up both the application and PostgreSQL in containers.

1. Run with Docker Compose:
```bash
make docker-compose-run
```

The service will be available at `http://localhost:{API_PORT}`.

## 🔍 Project Structure

```
url_alias_service/
├── src/                    # Source code
│   ├── api/               # API endpoints and routers
│   ├── core/              # Core application components
│   ├── db/                # Database configuration
│   ├── models/            # SQLAlchemy models
│   ├── repositories/      # Data access layer
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic layer
│   ├── utils/             # Utility functions and helpers
│   ├── config.py          # Configuration settings
│   └── main.py           # Application entry point
├── tests/                 # Test files
│   ├── integration/      # Integration tests
│   ├── unit/            # Unit tests
│   └── fixtures/        # Test fixtures and utilities
├── .github/              # GitHub Actions workflows
├── docker/               # Docker-related files
├── Dockerfile           # Main Dockerfile
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── .pylintrc           # Pylint configuration
├── .pre-commit-config.yaml # Pre-commit hooks
└── makefile            # Make commands for common tasks
```

## 🚦 API Endpoints

### Health Check
- `GET /ping` - Health check endpoint (returns "pong")

### Authentication Endpoints
- `POST /api/v1/register` - Register a new user
  - Request: username, password (form-data)
  - Response: user information

- `POST /api/v1/token` - Obtain access and refresh tokens
  - Request: username, password (form-data)
  - Response: access_token, refresh_token

- `POST /api/v1/token/refresh` - Refresh access token
  - Request: refresh_token
  - Response: new access_token and refresh_token pair

### User Management
- `GET /api/v1/users/me` - Get current user information
  - Requires: Bearer token authentication
  - Response: user information

- `POST /api/v1/users/{user_id}/revoke_tokens` - Revoke all user tokens
  - Requires: Bearer token authentication
  - Response: confirmation message

### URL Management
- `POST /api/v1/urls` - Create a new short URL
  - Requires: Bearer token authentication
  - Request: original URL, optional expiration time, optional tag
  - Response: short URL information

- `GET /api/v1/urls` - Get list of user's URLs
  - Requires: Bearer token authentication
  - Query Parameters:
    - short_code: Filter by short code
    - original_url: Filter by original URL
    - is_active: Filter by active status
    - tag: Filter by tag
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
  - Response: List of URL information

- `PATCH /api/v1/urls/{short_code}` - Deactivate a short URL
  - Requires: Bearer token authentication
  - Response: confirmation message

- `GET /{short_code}` - Redirect to original URL
  - Public endpoint
  - Redirects to the original URL if valid and active

### Statistics
- `GET /api/v1/urls/stats` - Get URL click statistics
  - Requires: Bearer token authentication
  - Query Parameters:
    - short_code: Filter by short code
    - original_url: Filter by original URL
    - is_active: Filter by active status
    - tag: Filter by tag
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
  - Response: List of URLs with click statistics:
    - clicks_last_hour: Number of clicks in the last hour
    - clicks_last_day: Number of clicks in the last 24 hours

All protected endpoints require an Authorization header with a Bearer token:
```
Authorization: Bearer your_access_token
```

## 🧪 Testing

The project includes both unit and integration tests. You can run tests in several ways:

### Local Testing
Run tests using pytest locally:
```bash
make test
```

### Docker Testing
Run tests in a Docker container:
```bash
make docker-test
```

The project uses pytest with async support and includes:
- Unit tests for individual components
- Integration tests for API endpoints
- Fixtures for database and authentication
- Mocking of external services
- Async test client for FastAPI

## 📝 Code Quality

The project uses several tools to maintain code quality:

1. **Pre-commit hooks**: Run automatically before each commit
2. **Black**: Code formatting
3. **Pylint**: Code analysis
4. **isort**: Import sorting

To manually run code quality checks:
```bash
make format
make lint
```

## 🔒 Security

### Authentication and Authorization
- **JWT (JSON Web Token) Based Authentication**
  - Access and Refresh token system
  - Access tokens expire in 5 minutes
  - Refresh tokens expire in 30 minutes
  - Token versioning for immediate revocation
