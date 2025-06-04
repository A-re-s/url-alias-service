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

## 🔧 Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/A-re-s/url-alias-service.git
cd url_alias_service
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source venv/bin/activate  # for Linux/Mac
venv\Scripts\activate  # for Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with the following variables:
```env
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

SECRET_KEY=

API_PORT=
```

5. Run the application:
```bash
make run
```

### Docker Deployment

1. Set up environment variables:
Create a `.env` file with the following variables:
```env
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

SECRET_KEY=

API_PORT=
```
2. Build and run Docker container:
```bash
make docker-run
```

## 🔍 Project Structure

```
url_alias_service/
├── src/                    # Source code
│   ├── api/               # API endpoints
│   ├── db/                # Database models and connection
│   ├── models/            # Data models
│   ├── repositories/      # Data access layer
│   ├── schemas/           # Pydantic schemas
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration settings
│   └── main.py           # Application entry point
├── tests/                 # Test files
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
├── .pylintrc            # Pylint configuration
├── .pre-commit-config.yaml # Pre-commit hooks configuration
└── makefile             # Make commands for common tasks
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

Run tests using pytest:
```bash
make test
```

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
