# Frontend Page: Menu Display

**HTML File:** `Menu`

## Purpose

This page displays all available menu items, categorized for easy browsing by the restaurant staff. It allows users to see item names, descriptions, prices, and images.

## Key JavaScript Functionalities

- **Fetching Data:** Retrieves all menu items from the backend API on page load.
- **Dynamic Rendering:**
    - Groups fetched menu items by their `category` property (e.g., 'appetizer', 'main_course').
    - Renders each category as a distinct section with a heading.
    - Within each category, dynamically creates and displays cards for each menu item, showing its name, price, description, and image (if available).
- **Error Handling:** Displays messages if the menu fails to load or if no menu items are available.
- **Navigation:**
    - Sets the "Menu" icon in the bottom navigation bar to an 'active' state.
    - Provides a back button in the header to navigate to the previous page using browser history.

## API Interactions

-   **Endpoint:** `GET /api/menu_items`
    -   **Purpose:** To fetch all menu items for display.
    -   **Triggered by:** Page load (`DOMContentLoaded` event).

## Key DOM Elements / Logic Flow

-   **`menu-categories-container` (id):** The main `div` where all category headings and lists of menu items are dynamically inserted by JavaScript.
-   **`loading-error-message` (id):** A `div` used to display "Loading menu..." initially, and then any error messages if the API call fails, or "Menu is currently empty" if no items are returned.
-   **Logic Flow:**
    1.  On `DOMContentLoaded`, an initial "Loading..." message is shown.
    2.  A `fetch` request is made to `/api/menu_items`.
    3.  If successful, the JavaScript groups items by category (e.g., 'appetizer', 'main_course', 'dessert', 'beverage').
    4.  It then iterates through a predefined `categoryOrder` array to display known categories in a specific sequence. For each category:
        - An `<h2>` heading is created.
        - A `div` container for items of that category is created.
        - If items exist for that category, each item is rendered as a card (name, price, description, image) and appended.
        - If no items exist, a "No items in this category" message is shown under the heading.
    5.  Any categories returned by the API but not in `categoryOrder` are appended afterwards.
    6.  If the API call fails, an error message is displayed in `loading-error-message`.

## User Interactions

-   **Scrolling:** Users can scroll through the list of categories and menu items. The header ("Menu") remains sticky at the top.
-   **Back Button:** Clicking the back arrow in the header navigates to the previously viewed page.
-   **Navigation Bar:** Users can navigate to other sections of the application (Tables, Orders, Settings) using the fixed bottom navigation bar. The "Menu" icon is highlighted as active on this page.
