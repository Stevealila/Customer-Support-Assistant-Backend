FROM python:3.13-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==2.1.2

# Copy Poetry configuration
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . /app/

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]