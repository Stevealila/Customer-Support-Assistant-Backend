# Customer Support Assistant Backend

A FastAPI-based backend for a customer support assistant that can handle customer inquiries and use AI to generate helpful responses.

## Architecture Overview

This project follows a service-oriented architecture with the following components:

1. **API Layer**
   - FastAPI routes for handling HTTP requests
   - Pydantic schemas for request/response validation

2. **Service Layer**
   - Business logic implementation
   - Dependency injection for better testability
   - Integration with external services (Groq AI)

3. **Repository Layer**
   - Database access logic
   - Implementation of the Repository pattern for data persistence

4. **Database Layer**
   - SQLAlchemy async ORM models
   - Alembic for database migrations

## Design Patterns Used

1. **Repository Pattern**
   - Separates the data access logic from business logic
   - Makes testing easier through dependency injection
   - Implementation: `BaseRepository` and its derivatives

2. **Dependency Injection**
   - FastAPI's dependency system is used to inject services and repositories
   - Makes testing easier by allowing mock replacements
   - Implementation: `get_db`, `get_auth_service`, etc.

3. **Service Layer Pattern**
   - Encapsulates application business logic in dedicated services
   - Provides a clean separation between API routes and data access
   - Implementation: `AuthService`, `TicketService`, `AIService`

4. **Adapter Pattern**
   - Used in the AI integration to adapt external API to our application's needs
   - Implementation: `AIService` abstracts Groq API details

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **PostgreSQL**: Relational database
- **Groq API**: AI provider for generating responses
- **Docker**: Containerization

## Setup Instructions

### Environment Variables

Copy the `.env.example` file to `.env` and update the variables:

```bash
cp .env.example .env
```

Using Docker
bash# Build and start all services
docker-compose up -d

# Apply database migrations
docker-compose exec web alembic upgrade head

# View logs
docker-compose logs -f
Local Development
bash# Install dependencies
poetry install

# Apply database migrations
alembic upgrade head

# Run the server
uvicorn app.main:app --reload
API Documentation
Once the server is running, you can access the API documentation at:

Swagger UI: http://localhost:8000/api/v1/docs
ReDoc: http://localhost:8000/api/v1/redoc

Development Challenges and Solutions

Asynchronous Database Operations

Challenge: Managing connection pools and transaction scope with async SQLAlchemy
Solution: Used proper async session management with context managers


Streaming AI Responses

Challenge: Implementing Server-Sent Events while also saving the complete response
Solution: Used an iterator-based approach to gather full response while streaming


Authentication & Authorization

Challenge: Securing routes while maintaining proper resource access control
Solution: Implemented JWT-based authentication with role-based permissions



Future Improvements
With more time, I would enhance the project with:

Testing: Comprehensive unit and integration tests
Rate Limiting: To prevent API abuse
Improved Error Handling: More specific error responses and logging
Admin Dashboard: For monitoring and managing support tickets
Enhanced AI Context: Providing more ticket context to the AI for better responses
Webhook Support: For notifications when a ticket status changes
Caching: Redis implementation for frequently accessed data


## Running the Application

With all the files in place, you can now run the application using Docker:

```bash
# Create a .env file from the example
cp .env.example .env

# Edit the .env file and add your actual API keys

# Build and start the application
docker-compose up -d

# Apply migrations
docker-compose exec web alembic upgrade head
The API will be available at http://localhost:8000, and you can access the OpenAPI documentation at http://localhost:8000/api/v1/docs.