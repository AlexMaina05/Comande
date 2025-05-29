# Frontend Page: New Reservation Creation

**HTML File:** `NewReservation`

## Purpose

This page provides a form for restaurant staff to create new table reservations for customers. It captures necessary details like customer name, contact information, reservation time, and number of guests.

## Key JavaScript Functionalities

- **Form Input Capture:** Collects data entered by the user into various input fields (customer name, phone number, reservation time, number of guests, table number).
- **Client-Side Validation:**
    - Checks for required fields: `customer_name`, `reservation_time`, `num_guests`.
    - Validates the `reservation_time` format (expects 'YYYY-MM-DD HH:MM:SS').
    - Ensures `num_guests` (and `table_number` if provided) are positive integers.
    - Displays validation error messages inline next to the respective fields or in a general message area at the top of the form.
- **JSON Payload Construction:** Prepares a JSON object with the reservation data to be sent to the backend API.
- **Form Submission Handling:**
    - Listens for the `submit` event on the form.
    - Prevents the default browser form submission.
    - Implements a loading state for the submit button ("Salva") during API interaction (disables button, changes text to "Salvataggio...").
- **API Interaction:** Sends the reservation data via a `POST` request to the `/api/reservations` endpoint.
- **Feedback Handling:**
    - Displays success messages inline (e.g., "Prenotazione creata con successo! ID: X") upon successful reservation creation (HTTP 201). The form is then reset.
    - Displays error messages inline if the API returns an error (e.g., validation error from backend, server error) or if a network error occurs.
- **Navigation:**
    - Provides an "X" button in the header to navigate back to the main `Reservation` listing page.

## API Interactions

-   **Endpoint:** `POST /api/reservations`
    -   **Purpose:** To create a new reservation in the system.
    -   **Triggered by:** User submitting the new reservation form.
    -   **Payload:** JSON object containing `customer_name`, `phone_number`, `reservation_time`, `num_guests`, and optionally `table_number` and `status`.

## Key DOM Elements / Logic Flow

-   **`newReservationForm` (id):** The main `<form>` element.
-   **Input Field IDs:** `customer_name`, `phone_number`, `reservation_time`, `num_guests`, `table_number`.
-   **Error Span IDs:** `customer_name_error`, `reservation_time_error`, `num_guests_error`, `table_number_error` for displaying field-specific validation messages.
-   **`form-message-area` (id):** A `div` at the top of the form used for displaying general success or API error messages.
-   **`submitButton` (id):** The main submission button ("Salva").
-   **Logic Flow:**
    1.  User fills out the form fields.
    2.  User clicks the "Salva" (Submit) button.
    3.  JavaScript prevents default form submission.
    4.  All previous error/success messages are cleared.
    5.  Client-side validation is performed on required fields and formats. If invalid, messages are shown next to fields, and submission stops.
    6.  If valid, the submit button is disabled, its text changes to "Salvataggio...", and a general "Invio prenotazione..." message is shown.
    7.  A `fetch` `POST` request is made to `/api/reservations` with the form data as JSON.
    8.  On success (201), a success message is displayed in `form-message-area`, the form is reset.
    9.  On API error (e.g., 400, 500), the error message from the API response is displayed in `form-message-area`.
    10. On network error, a generic network error message is displayed.
    11. The submit button is re-enabled, and its text is restored.

## User Interactions

-   **Input Fields:** Users type reservation details into the respective text and number input fields.
-   **"Salva" (Save) Button:** User clicks this to submit the form and create the reservation. The button provides visual feedback during processing.
-   **"X" (Close) Button:** User clicks this to cancel creating a new reservation and return to the main reservation list page.
