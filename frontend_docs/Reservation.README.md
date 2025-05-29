# Frontend Page: Reservation Listing

**HTML File:** `Reservation`

## Purpose

This page serves as the main dashboard for viewing all current and upcoming table reservations. It provides a summarized list, allowing staff to quickly see scheduled reservations and navigate to their details.

## Key JavaScript Functionalities

- **Fetching Data:** Retrieves a list of all reservations from the backend API (`/api/reservations`) when the page loads.
- **Dynamic Rendering:**
    - Displays a "Loading reservations..." message initially.
    - If the API call fails, an error message is shown.
    - If no reservations exist, a "No reservations for today" (or similar) message is displayed.
    - For each reservation fetched, it dynamically creates an HTML element (a card-like structure) to display key information:
        - Formatted reservation time (e.g., "7:00 PM").
        - Customer name.
        - Table number (or "N/A" if not assigned).
        - Number of guests.
        - Reservation status.
- **Navigation:**
    - Each reservation item in the list is clickable, navigating the user to `ReservationDetails.html?id=<reservation_id>` for that specific reservation.
    - An "Add New Reservation" button (typically a "+" icon) links to `NewReservation.html`.
    - A back arrow in the header (if present) might refresh the page or link to a higher-level dashboard (currently refreshes).
- **Active Nav State:** Sets the "Tables" icon in the bottom navigation bar to an 'active' state.

## API Interactions

-   **Endpoint:** `GET /api/reservations`
    -   **Purpose:** To fetch a list of all existing reservations.
    -   **Triggered by:** Page load (`DOMContentLoaded` event).

## Key DOM Elements / Logic Flow

-   **`reservations-list-container` (id):** The main `div` where the "Today" heading and the list of reservation items are dynamically inserted by JavaScript.
-   **Logic Flow:**
    1.  On `DOMContentLoaded`, an initial "Caricamento prenotazioni..." (Loading reservations...) message is shown in `reservations-list-container`.
    2.  A `fetch` request is made to `/api/reservations`.
    3.  The `innerHTML` of `reservations-list-container` is cleared and a static "Today" heading is re-added.
    4.  If the fetch is successful:
        - If the returned list is empty, a "Nessuna prenotazione per oggi." (No reservations for today.) message is appended.
        - If reservations exist, the script iterates through them. For each reservation:
            - The `createReservationElement` function is called. This function:
                - Parses and formats `reservation_time` (e.g., to "HH:MM AM/PM").
                - Creates a `div` for the reservation item, populating it with formatted time, customer name, table number, guest count, and status.
                - Attaches a click event listener to this `div` to navigate to `ReservationDetails.html?id=<reservation_id>`.
            - The newly created element is appended to `reservations-list-container`.
    5.  If the `fetch` call fails, an error message is displayed within `reservations-list-container`.
    6.  The "Tables" navigation icon is set to active.

## User Interactions

-   **Viewing List:** Users scroll through the list of reservations.
-   **Viewing Details:** Users click on a specific reservation item to navigate to its detailed view (`ReservationDetails.html`).
-   **Adding Reservation:** Users click the "Add New Reservation" button (plus icon at the bottom) to go to the `NewReservation.html` page.
-   **Navigation Bar:** Users can navigate to other sections (Orders, Menu, Settings) using the fixed bottom navigation bar. The "Tables" icon is highlighted.
