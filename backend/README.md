# Restaurant Management System - Backend

This is the backend for the Restaurant Management System, built with Flask and Flask-SQLAlchemy.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1.  **Clone the repository (or navigate to the `backend` directory if you already have it):**
    ```bash
    # If you are in the root of the project
    cd backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```
    - On macOS and Linux:
      ```bash
      source venv/bin/activate
      ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

The application uses an SQLite database (`restaurant.db`). The database file will be automatically created in the `backend` directory when the application is run for the first time. The necessary tables will also be created automatically.

## Running the Application

1.  **Ensure your virtual environment is activated and you are in the `backend` directory.**

2.  **Run the Flask development server:**
    ```bash
    python app.py
    ```

3.  The application will start, and by default, it should be accessible at `http://127.0.0.1:5000/`. You should see a "Hello, World!" message.

## Project Structure

-   `app.py`: Main Flask application file, initializes the app and database.
-   `database.py`: Initializes the SQLAlchemy `db` object.
-   `requirements.txt`: Lists Python dependencies.
-   `restaurant.db`: SQLite database file (created automatically).
-   `models/`: Contains SQLAlchemy database model definitions.
-   `__init__.py`: Defines `User`, `MenuItem`, `Reservation`, `Order`, `OrderItem` models.
-   `routes/`: Intended for API route definitions (e.g., using Flask Blueprints).
-   `services/`: Intended for business logic.
-   `utils/`: Intended for utility functions.
