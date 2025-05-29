# Frontend Page: Manage Order Items

**HTML File:** `ManageOrder.html`

## Purpose

This page allows staff to manage the items within a specific order (either food or beverage) that is associated with a reservation. Users can add new items from a filtered menu, change quantities of existing items, add special requests, remove items, and see the running total for the order.

## Key JavaScript Functionalities

- **URL Parameter Parsing:** Retrieves `reservation_id` and `order_id` from the URL query string on page load. If either is missing, displays an error and halts.
- **Data Fetching:**
    - Fetches details of the specific order from `/api/orders/<order_id>`. This includes existing items in the order.
    - Fetches all menu items from `/api/menu_items`.
- **Dynamic Rendering & Filtering:**
    - Updates the page title to reflect the order type (Food/Beverage) and ID.
    - **Menu Items (`menu-items-container`):**
        - Filters the fetched menu items based on the `currentOrder.order_type`. If 'food', beverage categories are excluded. If 'beverage', only beverage categories are shown.
        - Renders the filtered menu items, each with its name, price, and an "Add" button.
    - **Current Order Items (`current-order-items-container`):**
        - Renders items currently part of the order. Each item displays:
            - Name and unit price.
            - Quantity controls: "+" and "-" buttons, and a direct input field for quantity.
            - A text input field for special requests with a "Save Req." button.
            - A "Remove" button.
- **Item Management Logic:**
    - **Add to Order:**
        - Clicking "Add" on a menu item:
            - If the item already exists in the order, its quantity is incremented by 1 (via `PUT /api/order_items/<item_id>`).
            - If it's a new item, it's added to the order with quantity 1 (via `POST /api/orders/<order_id>/items`).
    - **Quantity Change:**
        - Using "+/-" buttons or changing the quantity input directly for an item in the current order triggers a `PUT /api/order_items/<item_id>` request with the new quantity. Quantity is validated to be at least 1.
    - **Special Requests:**
        - Editing the special requests input and clicking its "Save Req." button triggers a `PUT /api/order_items/<item_id>` request with the updated `special_requests` text.
    - **Remove Item:**
        - Clicking the "Remove" button on an order item (after confirmation) triggers a `DELETE /api/order_items/<item_id>` request.
- **Order Total Calculation:**
    - After any change to order items (add, update quantity, remove), the total price of the order is recalculated (`sum(item.price * item.quantity)`) and displayed in `order-total` element.
- **User Feedback:** Provides inline messages in `action-feedback` div for success/error of item operations. Page-level errors (e.g., initial load) go to `error-message` div.
- **Navigation:** A "Back to Reservation Details" button links to `ReservationDetails.html?id=<reservation_id>`.

## API Interactions

-   **Endpoint:** `GET /api/orders/<order_id>`
    -   **Purpose:** To fetch the details of the specific order being managed, including its current items.
    -   **Triggered by:** Page load.
-   **Endpoint:** `GET /api/menu_items`
    -   **Purpose:** To fetch all available menu items, which are then filtered by the frontend based on the current order's type.
    -   **Triggered by:** Page load (after initial order details are fetched).
-   **Endpoint:** `POST /api/orders/<order_id>/items`
    -   **Purpose:** To add a new menu item to the current order.
    -   **Triggered by:** Clicking "Add" on a menu item that is not yet in the order.
    -   **Payload:** `{ "menu_item_id": <id>, "quantity": 1 }`.
-   **Endpoint:** `PUT /api/order_items/<item_id>`
    -   **Purpose:** To update an existing item in the order (quantity or special requests).
    -   **Triggered by:**
        - Changing quantity using "+/-" buttons or input field. (Payload: `{ "quantity": new_value }`)
        - Saving special requests. (Payload: `{ "special_requests": "text" }`)
        - Adding a menu item that already exists in the order (increments quantity). (Payload: `{ "quantity": current_quantity + 1 }`)
-   **Endpoint:** `DELETE /api/order_items/<item_id>`
    -   **Purpose:** To remove an item from the current order.
    -   **Triggered by:** Clicking the "Remove" button on an order item.

## Key DOM Elements / Logic Flow

-   **URL Parameters:** `reservation_id`, `order_id`.
-   **Containers:** `menu-items-container`, `current-order-items-container`.
-   **Display/Feedback:** `manage-order-title`, `order-total`, `error-message`, `action-feedback`.
-   **Logic Flow (Initial Load):**
    1.  Parse `reservation_id` and `order_id` from URL.
    2.  `fetchOrderDetails()`:
        - Fetches the order from `/api/orders/<order_id>`.
        - Stores it in `currentOrder`.
        - Updates title, renders current items, calculates total.
        - Calls `fetchAndRenderMenuItems(currentOrder.order_type)`.
    3.  `fetchAndRenderMenuItems()`:
        - Fetches all items from `/api/menu_items`.
        - Filters them based on `currentOrder.order_type`.
        - Calls `renderMenuItems()` to display them.
-   **Logic Flow (Item Interactions - e.g., Add, Update Qty, Remove):**
    1.  User interacts with a button/input for an item.
    2.  Appropriate event handler (`handleAddToOrder`, `handleQuantityChangeBtn`, etc.) is triggered.
    3.  Handler constructs payload and makes the relevant API call (`POST`, `PUT`, or `DELETE`).
    4.  On success of API call:
        - `fetchOrderDetails(true)` is called to re-fetch the entire order, re-render the current items list, re-calculate the total, and show a generic "Order updated" message (or a specific one from the handler).
    5.  On failure, an error message is shown in `actionFeedbackDiv`.

## User Interactions

-   **Adding Items:** Users click "Add" on items from the "Menu Items" list. If the item is already in the "Current Order", its quantity is incremented; otherwise, it's added as a new line item.
-   **Changing Quantity:** Users click "+" or "-" buttons or type into the quantity field for items in the "Current Order".
-   **Adding Special Requests:** Users type into the "Special requests..." field for an item and click "Save Req.".
-   **Removing Items:** Users click "Remove" on an item in the "Current Order" (after a confirmation prompt).
-   **Navigation:** Users click "Back to Reservation Details" to return to the details page for the current reservation.
