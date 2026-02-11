# TeamTask-Server

A lightweight FastAPI server for managing multi-user projects, built as an educational project to demonstrate modern Python web development practices.

## Features
- **RESTf API**: Clean CRUD operations for project and task management
- **OAuth 2.0 Authentication**: Implements Resource Owner Password Credentials grant type with JWT tokens
- **Async Database Operations**: SQLAlchemy ORM with async support for efficient database queries
- **Configuration Management**: Pydantic-settings for type-safe environment variable handling
- **Modern Python**: Built with Python 3.12 and modern async patterns

## Tech Stack
- **Framework**: FastAPI
- **ORM**: SQLAlchemy (async)
- **Authentication**: OAuth 2.0 + JWT
- **Settings**: Pydantic-settings
- **Package Manager**: uv

## Prerequisites
Before running this project, ensure you have:

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

## Installation & Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/IlyaSlesar/teamtask-server.git
   cd TeamTask-server
   ```
2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   **Edit and fill in all required fields**
   - Generate a secure JWT secret key:
     ```bash
     openssl rand -base64 32
     ```
     
   - Add database connection details
   
3. **Run the application**
   You can use `--port [port-number]` to configure a non-default port to run on. **Runs on port 8000** by default.
   ```bash
   uv run uvicorn main:app
   ```
   
4. **Access the API**
   - API will be available at `http://localhost:8000` (or other port configured by Uvicorn)
   - Docs will be available at `http://localhost:8000/docs`

## Project structure
```
teamtask-server/
├── main.py    # Entry point
├── .env       # Settings
├── api/       # Path operations and their dependencies
├── core/      # Settings and security definitions used throughout application
├── db/        # SQLAlchemy model and session definitions
├── schemas/   # Pydantic schemas used by API
```

## Development
This is an educational project demonstrating:
- Modern async Python web development
- JWT-based authentication flows
- Database ORM patterns with SQLAlchemy
- Environment-based configuration
- REST API design principles

## License
This project is licensed under the terms of the MIT license.
