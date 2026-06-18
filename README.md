# qurated-api-test

Take home test for qurated to build an api based on the openapi.yaml file provided. The api should be able to handle the endpoints and methods defined in the [openapi.yaml](planning/openapi.yaml) file, and return appropriate responses based on the request parameters and data. The api should also include error handling and validation for the input data.

## Project Dependencies

- Python 3.12
- Poetry for dependency management
- Docker to containerize the application
- pre-commit for code quality checks before committing code and pushing to the repository
- Makefile for running linting and code

## Description

The project is a RESTful API built using FastAPI that implements the endpoints and methods defined in the provided OpenAPI specification. The API is designed to handle requests and return appropriate responses based on the request parameters and data.
It also includes error handling and validation for the input data.

## Running the API in container

To run the API, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. execute the following command to build and run the Docker container:
   ```bash
   docker-compose up --build
   ```
4. The API will be accessible at `http://localhost:8000`.
5. The API documentation will be available at `http://localhost:8000/docs`.

## Running the API locally

To run the API locally without Docker, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the dependencies using Poetry
   ```bash
   poetry install --no-root
   ```
4. Run the API using the following command:
   ```bash
   poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
5. The API will be accessible at `http://localhost:8000`.
6. The API documentation will be available at `http://localhost:8000/docs`.

## Testing the API

Once application is running, you can test the API endpoints using tools like Postman, curl, or directly through the interactive API documentation available at `http://localhost:8000/docs`.
Below are the token and user credentials to test the API endpoints:

- User edit API token: "4212Hnasin"
- Accounts API token: "42saf2asin"
