# Restaurant Reservation and Ordering System

## Overview

This project is a comprehensive Restaurant Reservation and Ordering System designed for internal use within a restaurant. Its primary goal is to streamline and digitalize the processes of managing table reservations and customer orders, enhancing operational efficiency. The system allows staff to effortlessly create and track reservations, manage food and beverage orders for each table, and generate printable tickets for kitchen and bar staff.

The backend is built using Python with the Flask framework, providing a robust API. Data is stored and managed in an SQLite database. The frontend is developed with standard HTML, CSS (styled with Tailwind CSS via CDN), and vanilla JavaScript, ensuring a lightweight and accessible user interface.

## Features

This system offers a range of features to assist restaurant staff:

*   **Reservation Management:**
    *   Create new reservations with essential guest details, including name, phone number, date, time, and party size.
    *   View a comprehensive list of all upcoming and past reservations.
    *   Access detailed information for specific reservations, including linked orders.
    *   Modify or cancel existing reservations as needed.
*   **Dynamic Menu Display:**
    *   Browse menu items clearly categorized (e.g., Appetizers, Main Courses, Desserts, Beverages).
    *   View item details, including price and description.
*   **Order Management:**
    *   Initiate separate 'food' and 'beverage' orders linked directly to a customer's reservation.
    *   Easily add items from the dynamic menu to an active order.
    *   Modify quantities of items in an order or add special requests and notes for the kitchen/bar.
    *   Remove items from an order if necessary.
    *   View all items currently in an order, along with a running total of the cost.
    *   Update the status of an order (e.g., pending, preparing, ready, served, paid).
*   **Print Functionality:**
    *   Generate clear, printable HTML tickets for food and beverage orders separately, optimized for kitchen and bar staff.
    *   Print tickets include all relevant details: table number (via reservation), items, quantities, and special requests.

## Technical Stack

This project utilizes the following technologies, frameworks, and libraries:

**Backend:**

*   **Programming Language:** Python (3.7+)
*   **Framework:** Flask (for building the web application and API)
*   **Database ORM:** SQLAlchemy (for interacting with the SQLite database)
*   **Database:** SQLite (a lightweight, file-based SQL database)
*   **API Development:** Flask Blueprints (for modular API route organization)
*   **CORS Handling:** Flask-CORS (for managing Cross-Origin Resource Sharing)
*   **Testing:** Pytest (for unit and integration testing of backend API endpoints)

**Frontend:**

*   **Markup:** HTML5
*   **Styling:** CSS3, primarily utilizing Tailwind CSS (v2.x via CDN for rapid UI development)
*   **JavaScript:** Vanilla JavaScript (ES6+ features) for client-side logic, DOM manipulation, and API interactions (e.g., using `fetch`). No frontend frameworks are currently used.

**Development Environment & Tooling:**

*   **Version Control:** Git
*   **Virtual Environments:** `venv` (for Python dependency management)
*   **Package Management:** `pip` (for Python packages)

## Application Workflow/Usage (Illustrative Scenarios)

This section outlines typical ways restaurant staff might interact with the system:

1.  **Checking and Adding Reservations:**
    *   A staff member typically starts their day by opening `Reservation.html` in their web browser. This page fetches and displays a list of all current and upcoming reservations by calling the `GET /api/reservations` endpoint.
    *   If a guest calls to book a table, the staff member navigates to `NewReservation.html`. They fill in the guest's details (name, phone, party size, date, time) and submit the form. This action triggers a `POST /api/reservations` request to the backend, saving the new booking.

2.  **Managing an Arriving Guest's Order:**
    *   When guests with a reservation arrive, the staff can find their booking in `Reservation.html` and click on it to view details, which loads `ReservationDetails.html` (using `GET /api/reservations/<reservation_id>`).
    *   From the `ReservationDetails.html` page, the staff can initiate a new food or beverage order. Clicking "Add Food Order" or "Add Beverage Order" might first create an order shell (`POST /api/reservations/<res_id>/orders`) and then navigate them to `ManageOrder.html`.
    *   In `ManageOrder.html`, menu items are dynamically loaded from the backend (`GET /api/menu_items`). Staff add items to the order, specify quantities, and include any special requests. Each item added is sent via `POST /api/orders/<order_id>/items`, and modifications might use `PUT /api/order_items/<item_id>`.
    *   The running total for the order is displayed on this page.

3.  **Sending Orders to Kitchen/Bar:**
    *   Once an order (or part of it) is finalized, the staff can generate printable tickets. From `ReservationDetails.html` or `ManageOrder.html`, there will be options to print.
    *   This action calls the `GET /api/orders/<order_id>/print` endpoint (potentially with `?type=food` or `?type=beverage` query parameters). The backend returns an HTML page formatted for printing, which is then displayed in a new tab or processed by the browser's print dialog.

4.  **Viewing Menu:**
    *   At any time, staff can open `Menu.html` to view all available menu items, categorized for easy browsing. This page fetches its data from `GET /api/menu_items`.

This workflow demonstrates how the frontend HTML pages interact with the backend API endpoints to provide a seamless experience for managing reservations and orders within the restaurant.

## Project Structure

The project is organized as follows:

*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.
*   `README.md`: (This file) The main documentation for the project.
*   `Menu.html`: HTML page for displaying the restaurant menu.
*   `NewReservation.html`: HTML page for creating a new reservation.
*   `Order.html`: An HTML page, primarily used as a template or for specific order views (primary order management is via `ManageOrder.html` and `ReservationDetails.html`).
*   `Reservation.html`: HTML page for listing all current and past reservations.
*   `ReservationDetails.html`: HTML page displaying detailed information for a specific reservation, including associated orders.
*   `ManageOrder.html`: HTML page dedicated to adding, editing, and managing items within a specific food or beverage order.
*   `frontend_docs/`: Contains detailed READMEs or documentation for specific frontend components, pages, or JavaScript interactions. This directory helps in understanding the intricacies of particular frontend features.
*   `backend/`: Contains the entire Flask backend application.
    *   `README.md`: Provides detailed documentation specific to the backend module.
    *   `app.py`: The main Flask application file. It initializes the Flask app, configures the database (SQLAlchemy), and registers all API route blueprints. It also includes logic to create database tables if they don't exist on startup.
    *   `database.py`: Defines and provides the shared SQLAlchemy `db` object, ensuring a single instance is used throughout the backend application.
    *   `models/`: This directory (typically `models/__init__.py`) contains SQLAlchemy model definitions (e.g., `User`, `MenuItem`, `Reservation`, `Order`, `OrderItem`) which map Python objects to database tables.
    *   `routes/`: Contains Flask Blueprints that organize API endpoints. Each file (e.g., `menu_routes.py`, `order_routes.py`, `reservation_routes.py`) groups routes for a specific resource.
    *   `tests/`: Contains all backend unit and integration tests written using the Pytest framework.
        *   `conftest.py`: Pytest configuration file; sets up common fixtures for tests, such as the test application instance and an in-memory database.
        *   `test_*.py`: Individual test files, typically one for each API module, containing specific test cases for the endpoints.
    *   `requirements.txt`: Lists all Python dependencies required for the backend (e.g., Flask, Flask-SQLAlchemy, pytest).
    *   `restaurant.db`: The SQLite database file. This file is automatically created in the `backend/` directory by SQLAlchemy when the application runs for the first time if it doesn't already exist.

## Setup and Running the Application

Follow these steps to set up and run the Restaurant Reservation and Ordering System:

### Backend Setup

1.  **Prerequisites:**
    *   Ensure Python 3.7+ is installed on your system.
2.  **Navigate to Backend Directory:**
    ```bash
    cd backend
    ```
3.  **Create and Activate a Virtual Environment (Highly Recommended):**
    *   This isolates project dependencies.
    ```bash
    python -m venv venv
    ```
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
4.  **Install Dependencies:**
    *   With the virtual environment activated, install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run the Flask Development Server:**
    ```bash
    flask run
    ```
    *   Alternatively, you can use:
    ```bash
    python app.py
    ```
6.  **Database Initialization:**
    *   Upon the first run, the SQLite database file (`restaurant.db`) will be automatically created in the `backend` directory.
7.  **Accessing the Backend:**
    *   The backend API will typically be available at `http://127.0.0.1:5000`. You should see a confirmation message like "Hello, World! The Restaurant API is active..." if you open this URL in a browser or use a tool like Postman.

### Frontend Setup

1.  **No Build Step Required:**
    *   The frontend consists of static HTML, CSS (via Tailwind CDN), and JavaScript files. No compilation or bundling process is needed.
2.  **Ensure Backend is Running:**
    *   The frontend pages rely on the backend API for data. Make sure the backend server is running before attempting to use the frontend.
3.  **Open HTML Files in Browser:**
    *   Navigate to the project's root directory.
    *   Open the desired HTML file directly in your web browser (e.g., `Reservation.html` to view reservations, or `Menu.html` to see the menu).
4.  **JavaScript Dependency:**
    *   Ensure your browser has JavaScript enabled, as it's used for dynamic content loading and interaction with the backend API.

### Running Backend Tests

1.  **Navigate to Backend Directory:**
    ```bash
    cd backend
    ```
2.  **Activate Virtual Environment:**
    *   If not already active, activate your virtual environment (see Backend Setup).
3.  **Ensure Test Dependencies are Installed:**
    *   `pytest` is included in `requirements.txt`.
4.  **Run Tests:**
    *   Execute the following command:
    ```bash
    python -m pytest
    ```
    *   The tests will run using a separate in-memory SQLite database (as configured in `tests/conftest.py`) to avoid interfering with your development database.

## API Endpoint Overview

The backend provides several API endpoints to manage resources. For detailed request/response formats and interactive testing, consider using tools like Postman or referring to the frontend JavaScript files and backend test files (`backend/tests/test_*.py`) for examples of API interactions.

*   **Reservations:**
    *   `POST /api/reservations`: Creates a new reservation. Expects JSON payload with guest details.
    *   `GET /api/reservations`: Retrieves a list of all reservations. Supports filtering by date.
    *   `GET /api/reservations/<reservation_id>`: Fetches details for a specific reservation by its ID.
    *   `PUT /api/reservations/<reservation_id>`: Updates an existing reservation (e.g., guest details, time).
    *   `DELETE /api/reservations/<reservation_id>`: Deletes a specific reservation.
*   **Menu Items:**
    *   `POST /api/menu_items`: Adds a new item to the menu. (Primarily for admin/setup)
    *   `GET /api/menu_items`: Retrieves a list of all menu items. Supports filtering by `category` (e.g., `/api/menu_items?category=Main Course`).
*   **Orders:**
    *   `POST /api/reservations/<reservation_id>/orders`: Creates a new order (specify `order_type`: "food" or "beverage") associated with a given reservation.
    *   `GET /api/orders/<order_id>`: Retrieves detailed information about a specific order, including all its items and their details.
    *   `POST /api/orders/<order_id>/items`: Adds a menu item to a specific order. Expects menu item ID, quantity, and optional special requests.
    *   `PUT /api/order_items/<item_id>`: Updates an item within an order (e.g., change quantity, modify special requests).
    *   `DELETE /api/order_items/<item_id>`: Removes a specific item from an order.
    *   `PUT /api/orders/<order_id>`: Updates the status of an order (e.g., "preparing", "served", "paid").
*   **Printing:**
    *   `GET /api/orders/<order_id>/print`: Generates a printable HTML representation of an order. Use query parameter `?type=food` or `?type=beverage` to get a filtered ticket for either food or beverage items specifically.

(Further details on request/response payloads can be found by examining the backend route implementations in `backend/routes/` and the frontend JavaScript files that interact with these endpoints.)

## NAS Deployment Guide

This guide provides instructions for deploying the Restaurant Reservation and Ordering System (Flask backend + static frontend) on a Network Attached Storage (NAS) device. Running the application on a NAS offers benefits like local hosting, direct data control, and an always-on solution for your restaurant.

Deployment methods can vary based on your NAS device's capabilities, specifically its operating system (e.g., Synology DSM, QNAP QTS, TrueNAS, or a generic Linux distribution) and whether it supports Docker.

### General Prerequisites for NAS Deployment

Before you begin, ensure you have the following:

*   **Network Access:** Your computer and the NAS must be on the same network.
*   **Administrative Access:** You'll need administrator privileges for your NAS to install software, configure settings, and manage services.
*   **Sufficient Storage:** Ensure your NAS has enough free space for the application files, Python environment (if applicable), Docker images (if applicable), and the `restaurant.db` database.
*   **NAS Operating System Familiarity:** A basic understanding of your NAS's operating system and how to access its command line (usually via SSH) or package manager will be helpful.

### Method 1: Running Backend Directly with Python on NAS

This method is suitable for NAS devices that provide shell access (SSH) and allow the installation of Python and related tools.

**Steps:**

1.  **Connect to NAS via SSH:**
    *   Find your NAS's IP address (e.g., from your router or NAS admin interface).
    *   Use an SSH client to connect. For example, on macOS/Linux:
        ```bash
        ssh your_nas_username@<NAS_IP_Address>
        ```
    *   For Windows, you can use PuTTY or the built-in SSH client in PowerShell/Command Prompt.

2.  **Install Python:**
    *   Check if Python 3.7+ is already installed:
        ```bash
        python3 --version
        ```
    *   If not installed or if the version is too old, install Python 3.7+ through your NAS's package manager (e.g., `apt-get install python3 python3-pip python3-venv` on Debian-based systems, `ipkg install python3`, or via Entware/Optware). Consult your NAS documentation for specific instructions. Compiling from source is an option but is more advanced.

3.  **Ensure `pip` and `venv` are Available:**
    *   `pip` (Python package installer) and `venv` (for virtual environments) are typically included with Python 3.7+. Verify with:
        ```bash
        python3 -m pip --version
        python3 -m venv -h
        ```

4.  **Clone or Upload Repository:**
    *   If your NAS has `git` installed:
        ```bash
        git clone <repository_url>
        cd <repository_directory_name>
        ```
    *   Alternatively, download the project as a ZIP file and upload it to a directory on your NAS, then unzip it.

5.  **Navigate to Backend Directory:**
    ```bash
    cd backend
    ```

6.  **Create and Activate Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *(Note: Activation command might differ slightly based on your NAS shell environment.)*

7.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

8.  **Initial Run & Database Creation:**
    *   Run the Flask application. Using `0.0.0.0` for the host makes the application accessible from other devices on your network, not just localhost on the NAS.
        ```bash
        flask run --host=0.0.0.0 --port=5000
        ```
    *   On the first run, the `restaurant.db` SQLite database file will be automatically created in the `backend/` directory.
    *   The backend will typically be available at `http://<NAS_IP_Address>:5000`.

9.  **Firewall Configuration:**
    *   If your NAS has a firewall enabled, ensure you create a rule to allow incoming traffic on the port the Flask app is using (e.g., TCP port 5000).

**Process Management (Keeping the Backend Running):**

Running `flask run` directly in an SSH session will terminate the application when you close the session. Here are a few ways to keep it running:

*   **Option A: `nohup` and `&` (Simple):**
    *   `nohup` (no hang-up) allows a command to keep running after you log out, and `&` runs it in the background. Output (including errors) will be redirected to `flask_app.log`.
        ```bash
        nohup flask run --host=0.0.0.0 --port=5000 > flask_app.log 2>&1 &
        ```
    *   To find the process ID (PID): `ps aux | grep flask`
    *   To stop the application: `kill <pid_of_flask_process>`

*   **Option B: `screen` or `tmux` (Recommended for manual management):**
    *   These terminal multiplexers allow you to create sessions that persist after you disconnect.
    *   Start a new session: `screen` or `tmux new-session -s flask_app`
    *   Run the Flask app command as usual within this session.
    *   Detach from the session (leaving it running): `Ctrl+A` then `D` for `screen`, or `Ctrl+B` then `D` for `tmux`.
    *   Reattach later: `screen -r` or `tmux attach-session -t flask_app`.

*   **Option C: Systemd / Supervisor / Init Scripts (Advanced & Robust):**
    *   For a more robust solution that can automatically restart the application if it crashes or on NAS reboot, consider using a process manager like `systemd` (common on modern Linux) or `supervisor`.
    *   This involves creating a service file that defines how to start, stop, and manage the Flask application. The specifics depend on your NAS OS. This is the most production-ready approach but requires more setup.

**Serving Frontend Files (with Python Backend):**

*   **Option A: Using NAS Built-in Web Server (Recommended):**
    *   Most NAS devices (e.g., Synology Web Station, QNAP Web Server) have a built-in web server.
    *   Configure this web server to serve the static HTML, CSS, and JavaScript files from the project's root directory (where `Reservation.html`, `Menu.html`, etc., are located).
    *   The frontend will then be accessible via `http://<NAS_IP_Address>/<configured_path>/` (e.g. `http://<NAS_IP_Address>/restaurant/Reservation.html`).
    *   API calls from the frontend (defined with relative paths like `/api/reservations`) will be directed to `http://<NAS_IP_Address>:5000/api/reservations` if the Flask app is running on port 5000. The application includes `Flask-CORS` which should handle cross-origin requests if the frontend and backend are served on different ports or subdomains by the NAS web server.

*   **Option B: Simple Python HTTP Server (for testing/simplicity):**
    *   If you don't want to configure the NAS web server, you can run a simple Python HTTP server from the project's root directory to serve the frontend files. This is generally not recommended for production.
        ```bash
        # In the project root directory (outside backend/)
        python3 -m http.server 8080
        ```
    *   Access frontend via `http://<NAS_IP_Address>:8080`.
    *   Potential CORS issues: If serving the frontend on a different port (e.g., 8080) than the backend (e.g., 5000), ensure `Flask-CORS` in the backend is correctly configured. The current setup uses `CORS(app, resources={r"/api/*": {"origins": "*"}})`, which should allow requests from any origin, simplifying this scenario.

### Method 2: Deploying Backend with Docker on NAS (Recommended)

This method is highly recommended if your NAS supports Docker (e.g., many Synology, QNAP models, or custom Linux NAS setups). Docker provides dependency isolation, easier updates, and a consistent running environment.

**Sample `Dockerfile` for the backend:**

Place the following content in a file named `Dockerfile` in the **root directory of the project**.

```dockerfile
# Dockerfile for Flask Backend
FROM python:3.9-slim

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory into the /app directory in the container
COPY backend/ ./

# The restaurant.db will be created in /app/restaurant.db inside the container.
# It's crucial to map a volume to /app or /app/restaurant.db from the NAS
# to ensure the database persists if the container is removed or recreated.
EXPOSE 5000

# Run the Flask application, accessible on the network
CMD ["flask", "run", "--host=0.0.0.0", "--port", "5000"]
```

**Steps:**

1.  **Install Docker on NAS:**
    *   Refer to your NAS manufacturer's documentation to install Docker (often available as a package in their app store/center).

2.  **Save `Dockerfile`:**
    *   Ensure the `Dockerfile` shown above is saved in the root directory of your project.

3.  **Build Docker Image:**
    *   Navigate to the project root directory (where the `Dockerfile` is) via SSH on your NAS.
    *   Build the image:
        ```bash
        docker build -t restaurant-app-backend .
        ```
        *   `-t restaurant-app-backend` tags the image with a memorable name.
        *   `.` indicates the build context is the current directory.

4.  **Run Docker Container:**
    *   Run the container with volume mapping for database persistence and port mapping:
        ```bash
        docker run -d \
                   -p 5001:5000 \
                   -v /path/on/nas/data/restaurant_app:/app \
                   restaurant-app-backend
        ```
    *   Explanation:
        *   `-d`: Runs the container in detached mode (in the background).
        *   `-p 5001:5000`: Maps port 5001 on your NAS to port 5000 inside the container. You'll access the backend via `http://<NAS_IP_Address>:5001`.
        *   `-v /path/on/nas/data/restaurant_app:/app`: **Crucial for data persistence.** This mounts the `/path/on/nas/data/restaurant_app` directory from your NAS into the `/app` directory inside the container. The `restaurant.db` file created by the app will then be stored on your NAS filesystem, preventing data loss if the container is stopped and removed. **Adjust `/path/on/nas/data/restaurant_app` to an actual path on your NAS.**
        *   `restaurant-app-backend`: The name of the image to run.

**Serving Frontend Files (with Dockerized Backend):**

*   **Option A: Using NAS Built-in Web Server (Recommended):**
    *   Same as in Method 1. Configure your NAS's web server to serve the static frontend files from the project root.
    *   API calls will target `http://<NAS_IP_Address>:<host_port_from_docker_run>` (e.g., `http://<NAS_IP_Address>:5001` if you used `-p 5001:5000`).

*   **Option B: Simple Python HTTP Server:**
    *   Same as in Method 1, but generally not needed if your NAS has a web server.

*   **Option C: Multi-container Docker Setup (Advanced):**
    *   For a more integrated Docker setup, you could use Docker Compose. This would involve creating a `docker-compose.yml` file to define and manage both the Flask backend container and another container (e.g., based on Nginx or Apache) to serve the frontend files. The Nginx container could also act as a reverse proxy for the backend, allowing both frontend and backend to be accessed on the same port. This is a more complex but cleaner setup for larger applications.

### General NAS Deployment Considerations

*   **Database Backup:**
    *   The `restaurant.db` file (located in `backend/` for direct Python, or your mapped volume for Docker) is critical.
    *   Implement a regular backup strategy for this file using your NAS's backup tools or a manual process.

*   **Resource Monitoring:**
    *   Keep an eye on your NAS's CPU, RAM, and storage usage, especially when the application is under load. Flask with SQLite is generally lightweight.

*   **Network Configuration:**
    *   **NAS IP Address:** Ensure you know how to find your NAS's current IP address. Consider setting a static IP address for the NAS in your router settings for reliability.
    *   **Client Access:** Client devices (computers, tablets for accessing the frontend) must be on the same network as the NAS and able to reach its IP address and the configured ports.
    *   **External Access (Advanced & Use with Caution):** If you need to access the application from outside your local network, you might explore options like DDNS, port forwarding on your router, or a reverse proxy setup on your NAS. Be aware of the security implications of exposing applications to the internet and take appropriate measures (HTTPS, strong passwords, firewall).

*   **Security:**
    *   Keep your NAS operating system, Python, Docker, and any other related software up to date with security patches.
    *   Use strong, unique passwords for NAS administration, SSH access, and any application-level accounts.
    *   Only open necessary ports in your NAS firewall and router. Avoid exposing the application to the internet unless absolutely necessary and secured.

*   **Application Updates:**
    *   **Direct Python Method:**
        1.  Connect to NAS via SSH, navigate to the project directory.
        2.  `git pull` (if using git) or re-upload new files.
        3.  Activate virtual environment: `source backend/venv/bin/activate`.
        4.  Install any new/updated dependencies: `cd backend && pip install -r requirements.txt`.
        5.  Stop the old application process (e.g., `kill <pid>`, or stop from `screen`/`tmux`).
        6.  Restart the application using your chosen process management method.
    *   **Docker Method:**
        1.  Update code (e.g., `git pull` or re-upload files).
        2.  Rebuild the Docker image: `docker build -t restaurant-app-backend .` (from the project root).
        3.  Stop the currently running container: `docker stop <container_id_or_name>`.
        4.  Remove the old container: `docker rm <container_id_or_name>`.
        5.  Start a new container with the updated image using the same `docker run` command (ensure volume mapping is correct).

*   **Troubleshooting:**
    *   **Logs:**
        *   For direct Python: Check `flask_app.log` (if using `nohup` redirection) or console output within `screen`/`tmux`.
        *   For Docker: `docker logs <container_id_or_name>`.
    *   **Port Conflicts:** Ensure the port you're trying to use (e.g., 5000, 5001) is not already in use by another service on your NAS.
    *   **File Permissions:** The user running the Flask application (or the Docker container) needs write permissions for the directory where `restaurant.db` is stored.
    *   **CORS Issues:** If you encounter issues where the frontend cannot communicate with the backend API, double-check your origins. `Flask-CORS` is configured to be permissive (`origins: "*"` for `/api/*` routes), but complex NAS web server or reverse proxy setups might introduce their own headers or policies. Check browser developer console for specific error messages.

## Contributing

This is an internal tool, but suggestions for improvements are welcome. Please discuss any significant changes with the team or lead developer before implementation.

## License

This project is licensed under the MIT License. See the LICENSE file for details (if a LICENSE file is present, otherwise, this statement suffices for now).
