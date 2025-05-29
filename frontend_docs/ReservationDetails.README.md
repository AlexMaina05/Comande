# Frontend Page: Reservation Details

**HTML File:** `ReservationDetails`

## Purpose

This page displays comprehensive details for a single reservation. It shows customer information, reservation specifics (time, guests, table, status), and lists all associated food and beverage orders. From here, users can manage these orders or print them.

## Key JavaScript Functionalities

- **URL Parameter Parsing:** Retrieves the `reservation_id` from the URL query string (`?id=<reservation_id>`) on page load. If no ID is found, it displays an error.
- **Fetching Data:**
    - Fetches primary reservation details from `/api/reservations/<reservation_id>`. This initial fetch is expected to include a list of associated orders (e.g., `reservation.orders`).
    - **Fallback for Orders:** If `reservation.orders` is not directly provided in the reservation details response, it makes a subsequent call to `GET /api/orders` and filters them client-side by `reservation_id`.
- **Dynamic Rendering:**
    - Populates designated HTML elements with reservation details (customer name, number of guests, table number, formatted date and time, status).
    - Dynamically renders a list of orders associated with the reservation in the `orders-list-container`. Each order entry displays:
        - Order Type (e.g., "Food Order", "Beverage Order").
        - Order ID.
        - Number of items in the order (calculated from `order.items.length`).
        - Current status of the order.
        - A "Print" button.
- **Order Management Navigation:**
    - Provides "Manage Food Order" and "Manage Beverage Order" buttons.
    - When clicked:
        - Checks if an order of the specified type (`food` or `beverage`) already exists for the current reservation.
        - If it exists, navigates to `ManageOrder.html?reservation_id=<res_id>&order_id=<existing_order_id>`.
        - If it does NOT exist, it first makes a `POST` request to `/api/reservations/<reservation_id>/orders` to create a new order of that type.
        - On successful creation of the new order, the page refreshes its order list to display the new (empty) order, then navigates to `ManageOrder.html?reservation_id=<res_id>&order_id=<new_order_id>`.
- **Print Functionality:**
    - Each order in the list has a "Print" button.
    - Clicking "Print" fetches the printable HTML version of that order from `/api/orders/<order_id>/print`.
    - The received HTML content is then written into a new blank browser window/tab for printing.
    - Handles potential popup blocker issues and provides feedback.
- **Data Refresh on Page Show:** Includes a `pageshow` event listener to re-fetch all data if the page is loaded from the browser's back/forward cache, ensuring data consistency after returning from `ManageOrder.html`.
- **Error Handling:** Displays inline error messages if fetching reservation details or orders fails, or if creating a new order fails. Print errors are also handled with messages.

## API Interactions

-   **Endpoint:** `GET /api/reservations/<reservation_id>`
    -   **Purpose:** To fetch detailed information for a specific reservation, ideally including its associated orders.
    -   **Triggered by:** Page load, using `reservation_id` from URL.
-   **Endpoint:** `GET /api/orders` (Fallback)
    -   **Purpose:** To fetch all orders if they are not included in the `GET /api/reservations/<id>` response. The frontend then filters these by `reservation_id`.
    -   **Triggered by:** Page load, only if necessary after the primary reservation fetch.
-   **Endpoint:** `POST /api/reservations/<reservation_id>/orders`
    -   **Purpose:** To create a new 'food' or 'beverage' order for the current reservation if one doesn't already exist when a "Manage..." button is clicked.
    -   **Triggered by:** Clicking "Manage Food Order" or "Manage Beverage Order" if no corresponding order exists.
    -   **Payload:** `{ "order_type": "food" }` or `{ "order_type": "beverage" }`.
-   **Endpoint:** `GET /api/orders/<order_id>/print`
    -   **Purpose:** To retrieve a printable HTML representation of a specific order.
    -   **Triggered by:** Clicking the "Print" button for an individual order.

## Key DOM Elements / Logic Flow

-   **URL Parameter:** `id` (for `reservation_id`).
-   **Reservation Detail Elements:** `details-customer-name`, `details-num-guests`, `details-table-number`, `details-date`, `details-time`, `details-reservation-status`.
-   **Order Management Buttons:** `manage-food-order-btn`, `manage-beverage-order-btn`.
-   **Containers & Feedback:** `orders-list-container`, `reservation-fetch-error`, `orders-fetch-error`, `action-feedback` (for order creation), `print-message-area`.
-   **Logic Flow (Main):**
    1.  On `DOMContentLoaded` (and `pageshow` if from cache):
        - Get `reservation_id` from URL.
        - Call `mainFetchAndRender()`:
            - Display initial "Loading..." messages.
            - Fetch reservation data from `/api/reservations/<reservation_id>`.
            - Populate reservation detail elements.
            - If `reservation.orders` exists, call `displayOrders()`.
            - Else (fallback), fetch `/api/orders`, filter, then call `displayOrders()`.
            - Handle any fetch errors by showing messages in error divs.
-   **Logic Flow (`handleManageOrder(orderType)`):**
    1.  User clicks "Manage Food Order" or "Manage Beverage Order".
    2.  Buttons are temporarily disabled.
    3.  Check `fetchedReservationData.orders` for an existing order of `orderType`.
    4.  If found, navigate to `ManageOrder.html` with `reservation_id` and the found `order_id`.
    5.  If not found:
        - `POST` to `/api/reservations/<reservation_id>/orders` to create it.
        - On success, call `mainFetchAndRender()` to refresh the displayed orders list (now including the new empty order).
        - Display a success message.
        - Navigate to `ManageOrder.html` with `reservation_id` and the new `order_id`.
        - Handle creation errors.
    6.  Re-enable buttons if navigation does not occur.
-   **Logic Flow (`handlePrintOrder(event)`):**
    1.  User clicks a "Print" button on an order.
    2.  Display inline "Printing..." status.
    3.  `GET` HTML from `/api/orders/<order_id>/print`.
    4.  Open new window, write HTML, handle errors/popup blocker. Update inline status.

## User Interactions

-   **Viewing Details:** Users see reservation and associated order details upon page load.
-   **Managing Orders:**
    - Clicking "Manage Food Order" either takes them to manage an existing food order or creates one and then takes them to manage it.
    - Clicking "Manage Beverage Order" does the same for beverage orders.
-   **Printing Orders:** Users click the "Print" button next to an individual order to open a printable ticket in a new window/tab.
-   **Back Navigation:** Uses the browser's back functionality or the header's back arrow to return to the `Reservation` list. Data is refreshed if page is from cache.
