# This file will contain templating functions
from backend.models import Order, OrderItem # Added OrderItem as it's used in the function

def generate_order_html(order: Order, items_to_print: list, print_type_title: str) -> str:
    """
    Generates an HTML string representation of an order ticket.

    Args:
        order: The Order object.
        items_to_print: A list of OrderItem objects to include in the ticket.
        print_type_title: The title for the ticket (e.g., "Food Order", "Beverage Order").

    Returns:
        An HTML string.
    """
    timestamp = order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else 'N/A'
    # Access table number via the reservation relationship if it exists
    table_number = order.reservation.table_number if order.reservation else 'N/A'

    # Start building the HTML string
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Order Ticket - {print_type_title} - Order #{order.id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }}
            .ticket {{ border: 1px solid #000; padding: 10px; width: 280px; margin: auto; }} /* Common thermal printer width */
            h1 {{ text-align: center; margin-top: 0; font-size: 1.3em; }}
            p {{ margin: 3px 0; }}
            ul {{ list-style-type: none; padding: 0; margin:0; }}
            li {{ margin-bottom: 5px; border-bottom: 1px dashed #ccc; padding-bottom: 3px; }}
            li:last-child {{ border-bottom: none; }}
            .item-name {{ font-weight: bold; }}
            .item-details {{ display: flex; justify-content: space-between; }}
            .special-requests {{ font-style: italic; font-size: 0.9em; color: #555; margin-left: 8px;}}
        </style>
    </head>
    <body>
        <div class="ticket">
            <h1>{print_type_title}</h1>
            <p><strong>Order ID:</strong> {order.id}</p>
            <p><strong>Table #:</strong> {table_number}</p>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <hr>
            <p><strong>Items:</strong></p>
            <ul>
    """

    # Add each item to the HTML list
    for item in items_to_print:
        html += f"""
                <li>
                    <div class="item-details">
                        <span class="item-name">{item.quantity}x {item.menu_item.name if item.menu_item else 'N/A'}</span>
                    </div>
                    {f'<p class="special-requests"><em>Note: {item.special_requests}</em></p>' if item.special_requests else ''}
                </li>
        """

    html += """
            </ul>
        </div>
    </body>
    </html>
    """
    return html
