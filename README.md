# Restaurant Reservation and Ordering System

## Overview
A web application for internal restaurant use to manage table reservations and customer orders.
Handles creation of reservations, separate ordering for food and beverages, and generation of printable order tickets.
Backend built with Python (Flask) and SQLite. Frontend uses HTML, Tailwind CSS, and vanilla JavaScript.

## Features
- **Reservation Management:** Create new reservations, view a list of all reservations, view details of specific reservations.
- **Dynamic Menu Display:** View menu items categorized (e.g., Appetizers, Main Courses, Desserts, Beverages).
- **Order Management:**
    - Create separate 'food' and 'beverage' orders associated with a reservation.
    - Add items from the menu to an order.
    - Modify item quantities and add special requests.
    - Remove items from an order.
    - View items currently in an order with a running total.
- **Print Functionality:** Generate printable HTML tickets for food and beverage orders separately.

## Project Structure
- `README.md` (This file)
- `Menu` (HTML file for Menu page)
- `NewReservation` (HTML file for New Reservation page)
- `Order` (HTML file, currently less used due to order management in ReservationDetails/ManageOrder)
- `Reservation` (HTML file for listing Reservations)
- `ReservationDetails` (HTML file for Reservation Details page)
- `ManageOrder.html` (HTML file for adding/editing items in an order)
- `backend/`: Contains the Flask backend application.
    - `app.py`: Main Flask application file, initializes DB and registers blueprints.
    - `database.py`: SQLAlchemy `db` instance.
    - `models/`: Defines SQLAlchemy database models (`User`, `MenuItem`, `Reservation`, `Order`, `OrderItem`).
    - `routes/`: Contains Flask Blueprints for API endpoints (`menu_routes.py`, `order_routes.py`, `reservation_routes.py`).
    - `tests/`: Contains Pytest unit tests for the backend API.
        - `conftest.py`: Pytest configuration and fixtures.
        - `test_*.py`: Test files for each API module.
    - `requirements.txt`: Python dependencies for the backend.
    - `restaurant.db`: SQLite database file (auto-created on first run in the `backend` directory).

## Setup and Running the Application

**Backend:**
- Requires Python 3.7+ (or as per current environment).
- Navigate to the `backend` directory: `cd backend`
- **Create and activate a virtual environment (recommended):**
  ```bash
  python -m venv venv
  # On Windows:
  # venv\Scripts\activate
  # On macOS/Linux:
  # source venv/bin/activate
  ```
- **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```
- **Run the Flask development server:**
  ```bash
  flask run
  # Or: python app.py
  ```
- The backend will typically be available at `http://127.0.0.1:5000`.
- The SQLite database (`restaurant.db`) will be automatically created in the `backend` directory.

**Frontend:**
- No build step is required.
- After starting the backend server, open the HTML files directly in your web browser.
- Recommended starting page: `Reservation` (or `Menu`).
- Ensure your browser has JavaScript enabled.

**Running Backend Tests:**
- Navigate to the `backend` directory: `cd backend`
- Ensure test dependencies are installed (e.g., `pytest` is in `requirements.txt`).
- Run:
  ```bash
  python -m pytest
  ```

## Notes for NAS Deployment
- This application uses a Python Flask backend and a file-based SQLite database.
- **NAS Requirements:**
    - Python 3.7+ (or compatible version).
    - Capability to install Python packages using `pip`.
    - (Recommended) Docker support on the NAS for easier deployment and dependency management. A `Dockerfile` would need to be created for this (currently not provided).
- **Database:** The `backend/restaurant.db` file is crucial. Ensure the directory where the backend application runs on the NAS is writable by the application so it can create/modify this file.
- **Frontend Files:** The HTML, CSS (Tailwind via CDN), and JavaScript files can be:
    - Served by a simple HTTP server application running on the NAS.
    - Accessed via direct file paths if the NAS and browser security settings permit (serving via HTTP is generally more reliable for API interactions to avoid Cross-Origin Resource Sharing (CORS) issues if the frontend and backend are served from different conceptual origins).
- **API Accessibility:** Ensure the frontend (running in users' browsers) can reach the backend API (running on the NAS) via the network. This might involve NAS firewall configuration or ensuring they are on the same local network.

## API Endpoint Overview
- **Reservations:**
    - `POST /api/reservations`: Create new reservation.
    - `GET /api/reservations`: List all reservations.
    - `GET /api/reservations/<id>`: Get specific reservation.
    - `PUT /api/reservations/<id>`: Update reservation.
    - `DELETE /api/reservations/<id>`: Delete reservation.
- **Menu Items:**
    - `POST /api/menu_items`: Create new menu item.
    - `GET /api/menu_items`: List menu items (supports `?category=` filter).
- **Orders:**
    - `POST /api/reservations/<res_id>/orders`: Create a new order (food/beverage) for a reservation.
    - `GET /api/orders/<order_id>`: Get details of a specific order, including its items.
    - `POST /api/orders/<order_id>/items`: Add an item to an order.
    - `PUT /api/order_items/<item_id>`: Update quantity/special requests of an order item.
    - `DELETE /api/order_items/<item_id>`: Remove an item from an order.
    - `PUT /api/orders/<order_id>`: Update order status.
- **Printing:**
    - `GET /api/orders/<order_id>/print`: Get printable HTML for an order (supports `?type=food/beverage` filter).
