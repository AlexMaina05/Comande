# Backend - Restaurant Reservation and Ordering System

## Overview
This directory houses the Python Flask backend application for the Restaurant Reservation and Ordering System.
Its core responsibilities include:
- Serving API requests from the frontend or other clients.
- Implementing the business logic for managing reservations, menu items, and customer orders.
- Handling all database interactions via SQLAlchemy with an SQLite database.

## Directory Structure

-   **`app.py`**: The main Flask application script. It configures the Flask app, initializes the SQLAlchemy database instance (`db.init_app(app)`), and registers all API route blueprints from the `routes/` directory. It also contains the logic to create database tables if they don't exist on startup (`db.create_all()`).
-   **`database.py`**: Defines and provides the shared SQLAlchemy `db` object (`db = SQLAlchemy()`). This is imported by `app.py` and model files to ensure a single instance is used throughout the application, preventing circular import issues.
-   **`models/`**: This directory (specifically `models/__init__.py` in the current structure) contains the SQLAlchemy model definitions. These classes (e.g., `User`, `Reservation`, `MenuItem`, `Order`, `OrderItem`) map Python objects to database tables and define their schemas and relationships.
-   **`routes/`**: Organizes API endpoints into Flask Blueprints. Each file in this directory (e.g., `reservation_routes.py`, `menu_routes.py`, `order_routes.py`) typically corresponds to a specific resource or functional area of the API.
-   **`tests/`**: Contains all backend unit and integration tests written using the `pytest` framework.
    -   `conftest.py`: Sets up common `pytest` fixtures used across multiple test files. This includes fixtures for the test application instance (`app`), a test client (`client`) to make requests to the app without running a live server, and a database fixture (`db`, `session`) that configures an in-memory SQLite database for testing and handles schema creation and teardown.
    -   `test_*.py`: Individual test files, typically one for each API module (e.g., `test_reservation_api.py`), containing specific test cases for the endpoints.
-   **`requirements.txt`**: Lists all Python dependencies required for the backend to run (e.g., Flask, Flask-SQLAlchemy, pytest). These can be installed using `pip install -r requirements.txt`.
-   **`restaurant.db`**: The SQLite database file. This file is automatically created in the `backend` directory by SQLAlchemy when the application runs for the first time if it doesn't already exist (due to the `db.create_all()` call in `app.py`).

## Setup and Running

Refer to the main project `README.md` (in the parent directory) for initial Python and virtual environment setup instructions.

**To run the backend server:**
```bash
# Navigate to the backend directory from the project root
cd backend

# Ensure your virtual environment is activated
# On macOS/Linux:
# source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies (if not already done or if requirements.txt has changed)
pip install -r requirements.txt

# Run the Flask development server
flask run
# Alternatively, you might run: python app.py
```
- The server typically runs on `http://127.0.0.1:5000/`.
- A message like "Hello, World! The Restaurant API is active..." should be visible if you open this URL in a browser.

## Database
- The application uses SQLite as its database, which is a file-based system.
- The database file is named `restaurant.db` and is automatically created and located in the `backend` directory.
- Database tables are automatically created based on the SQLAlchemy models defined in `models/__init__.py` when the application first starts (specifically, when `db.create_all()` is executed within the app context in `app.py`).
- **Development Note:** If you need to reset the database (e.g., due to model changes not handled by simple `create_all`), you can delete the `restaurant.db` file. Restarting the application will then generate a new, empty database. For production environments or more complex schema changes, a database migration tool like Flask-Migrate (which uses Alembic) would be recommended.

## Testing
- Unit and integration tests for the backend API are written using the `pytest` framework.
- Test files are located in the `backend/tests/` directory.
- **To run tests:**
  ```bash
  # Navigate to the backend directory from the project root
  cd backend

  # Ensure pytest and other dependencies are installed (they are in requirements.txt)
  # (Activate your virtual environment if you haven't already)

  # Run pytest
  python -m pytest
  ```
- The tests are configured (in `tests/conftest.py`) to run against a dedicated in-memory SQLite database. This ensures that tests are fast, repeatable, and do not interfere with the development database (`restaurant.db`). Each test function typically runs in its own transaction, which is rolled back after completion to maintain test isolation.

## API Endpoints
A comprehensive list and detailed description of all available API endpoints (including request/response formats) can be found in the main project `README.md` located in the parent directory of this `backend` folder.

## Notes
- The backend uses Flask Blueprints to organize routes for modularity, making it easier to manage different parts of the API (reservations, menu, orders).
- SQLAlchemy is used as the ORM (Object-Relational Mapper) to interact with the SQLite database, allowing database operations to be performed using Python objects and methods.
- Error handling in API routes generally returns JSON responses with an "error" key and a descriptive message, along with appropriate HTTP status codes.
