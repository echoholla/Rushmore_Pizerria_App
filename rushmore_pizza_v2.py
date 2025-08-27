import json  # To handle reading and writing order data
from datetime import datetime  # To record the timestamp of orders
import os  # To interact with the operating system (e.g. checking if a file exists)
import random  # To generate random numbers for delivery estimates and order numbers

# -------------------------------
# Pizza Menu - Name and price of menu
# -------------------------------
pizza_data = {
    "1": {"name": "Classic", "price": 3.4},
    "2": {"name": "Chicken", "price": 4.5},
    "3": {"name": "Pepperoni", "price": 4.0},
    "4": {"name": "Deluxe", "price": 6.0},
    "5": {"name": "Vegetable", "price": 4.0},
    "6": {"name": "Chocolate", "price": 12.0},
    "7": {"name": "Cheese", "price": 5.0},
    "8": {"name": "Hawaiian", "price": 7.0},
    "9": {"name": "Greek", "price": 8.0}
}

# -------------------------------
# Extras Menu - Each category has items with prices
# -------------------------------
extras = {
    "sides": {
        "Fries": 1.50,
        "Potato Wedges": 2.00,
        "Chicken Strippers": 2.50,
        "Garlic Bread": 1.75,
        "Chicken Wings": 3.00
    },
    "drinks": {
        "Diet Cola": 1.20,
        "Coca-Cola": 1.30,
        "Fanta": 1.25,
        "Barr": 1.00,
        "Monster": 2.00,
        "Sprite": 1.25,
        "7-up": 1.25,
        "Water": 0.90,
        "Juice": 1.50
    },
    "toppings": {
        "Onions": 0.50,
        "Sweet Corn": 0.50,
        "Jalapeno": 0.60,
        "Olives": 0.60,
        "Mushrooms": 0.70,
        "Bacon": 1.00,
        "Cheese": 0.80
    },
    "dips": {
        "Herb": 0.50,
        "BBQ": 0.50,
        "RedHot": 0.50,
        "Sweet Icing": 0.50,
        "Garlic": 0.50,
        "Salad Cream": 0.50
    },
    "dessert": {
        "Vanilla": 2.50,
        "Cookies": 1.80,
        "Cheesecake": 3.00,
        "Jam Tart": 1.50,
        "Semolina": 1.70,
        "Gateaux": 3.20,
        "Strawberry Mousse": 2.80
    }
}

# -------------------------------
# File paths for saving data
# -------------------------------
ORDERDB_FILE = 'pizza_orders.json'  # File to store all pizza orders
USER_INFO_FILE = 'user_info.json'   # File to store saved user delivery information

# -------------------------------
# Function to save an order to JSON file
# -------------------------------
def save_order_to_json(pizza_type, order_type, quantity, price, discount, extras):
    order = {
        'order_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Capture current date & time
        'pizza_type': pizza_type,  # Name of the pizza ordered
        'order_type': order_type,  # Box or Slice
        'quantity': quantity,  # Number of items
        'total_price': price,  # Final price after any discount
        'discount_applied': discount,  # Whether a discount was used
        'extras': extras  # Any extras (sides, drinks, etc.)
    }

    # If file exists, read it and append the new order
    if os.path.exists(ORDERDB_FILE):
        with open(ORDERDB_FILE, 'r+', encoding='utf-8') as file:
            try:
                data = json.load(file)  # Load existing orders
            except json.JSONDecodeError:
                data = []  # If empty or invalid, start fresh
            data.append(order)  # Add new order to list
            file.seek(0)  # Move cursor to the start before writing
            json.dump(data, file, indent=4)  # Save updated list
    else:
        # If file doesn't exist, create and add the first order
        with open(ORDERDB_FILE, 'w', encoding='utf-8') as file:
            json.dump([order], file, indent=4)

# -------------------------------
# Retrieve previously saved user delivery info
# -------------------------------
def get_saved_user_info():
    if os.path.exists(USER_INFO_FILE):
        with open(USER_INFO_FILE, 'r') as file:
            return json.load(file)  # Return saved delivery data
    return None  # No file means no saved info

# -------------------------------
# Save user delivery info for future reuse
# -------------------------------
def save_user_info(address, postcode, email):
    data = {
        "address": address, 
        "postcode": postcode, 
        "email": email
    }
    with open(USER_INFO_FILE, 'w') as file:
        json.dump(data, file, indent=4)  # Save as formatted JSON

# -------------------------------
# Calculate final price including any discount
# -------------------------------
def calculate_payment(price, quantity, discount_rate=0.0):
    total = price * quantity  # Base price
    discount = total * discount_rate  # Amount of discount
    return total - discount  # Final price after discount

# -------------------------------
# Allow user to select extras (sides, drinks, etc.)
# -------------------------------
def select_extras():
    chosen_extras = []  # List to store selected extras
    total_extras = 0.0  # Track total cost of extras

    print("\nWould you like any extras like sides, toppings, etc. with your order?")

    # Loop through each extras category
    for category, items in extras.items():
        print(f"\n{category.capitalize()} options:")  # Print the category header

        # Print each item in that category
        for item, price in items.items():
            print(f" - {item}: ${price:.2f}")

        while True:
            # Ask for user input (case-insensitive)
            choice = input(f"Select a {category} by name (or press Enter to skip): ").strip().lower()

            if choice == "":
                break  # Skip this category if user presses Enter

            # Search for the matching item (case-insensitive match)
            matched_item = next((item for item in items if item.lower() == choice), None)

            if matched_item:
                chosen_extras.append({"category": category, "name": matched_item, "price": items[matched_item]})
                total_extras += items[matched_item]
                print(f"> {matched_item} added.")
                break  # Exit inner loop after a valid selection
            else:
                print("Invalid item. Please enter the name exactly as shown.")

    return chosen_extras, total_extras  # Return both the list of extras and total cost

# -------------------------------
# Ask if user wants to make it a full meal
# -------------------------------
def full_meal():
    # Ask user if they want extras
    response = input("\nWould you like to make it a full meal with sides, drinks, or dessert? (yes/no or y/n): ").strip().lower()

    if response in ("yes", "y"):
        return select_extras()  # Call function to handle extra selections
    elif response in ("no", "n"):
        return [], 0.0  # Return empty list and 0 if no extras
    else:
        print("Invalid input. Please type yes/y or no/n.")
        return full_meal()  # Retry until user gives valid input

# -------------------------------
# Handle takeout or delivery and optionally save user info
# -------------------------------
def handle_delivery_option():
    while True:
        delivery_type = input("\nIs this order for Takeout or Delivery? (T/D): ").strip().upper()

        if delivery_type == "T":
            print("Your order will be ready for pickup shortly!")
            return "Takeout", None, None, None  # Takeout does not need address info

        elif delivery_type == "D":
            saved_info = get_saved_user_info()  # Try to load saved user info

            use_saved = False
            if saved_info:
                print("\nWe found saved delivery info:")
                print(f" - Address: {saved_info['address']}")
                print(f" - Postcode: {saved_info['postcode']}")
                print(f" - Email: {saved_info['email']}")
                use_saved = input("Use saved info? (Y/N): ").strip().lower() in ["y", "yes"]

            # If using saved info, skip asking
            if use_saved:
                address = saved_info["address"]
                postcode = saved_info["postcode"]
                email = saved_info["email"]
            else:
                address = input("Please input your delivery address: ").strip()
                postcode = input("Please input your postcode: ").strip()
                email = input("Please input your email address for the receipt: ").strip()
                save_user_info(address, postcode, email)  # Save new delivery info

            eta = random.randint(15, 45)  # Simulated delivery time
            print(f"Estimated time of delivery to {address} is {eta} minutes")
            return "Delivery", address, postcode, email  # Return all delivery details

        else:
            print("Please choose 'T' for Takeout or 'D' for Delivery")

# -------------------------------
# Generate and print the receipt
# -------------------------------
def generate_receipt(order_id, pizza_type, quantity, order_type, total_price, discount_applied, delivery_type, extras, postcode=None, email=None, pizza_total=None):
    print("-" * 60)
    print("ORDER RECEIPT".center(60))
    print("-" * 60)
    print(f"Order Number: {order_id}")
    print(f"Order Type: {order_type}")
    print(f"Pizza Type: {pizza_type}")
    print(f"Quantity: {quantity}")
    print(f"Discount Applied: {'Yes' if discount_applied else 'No'}")
    print(f"Delivery Type: {delivery_type}")
    print()

    # Extras section with individual prices
     # Print pizza subtotal
    if pizza_total is not None:
        print(f"{'Subtotal for Pizza:':<35} ${pizza_total:.2f}")

    # Extras section
    if extras:
        print("Extras:")
        extras_total = 0.0
        for extra in extras:
            print(f"  - {extra['category'].capitalize()} | {extra['name']:<20} ${extra['price']:.2f}")
            extras_total += extra['price']
        print(f"{'Subtotal for Extras:':<35} ${extras_total:.2f}")
    else:
        print("Extras: None")

    print(f"{'Total Price:':<35} ${total_price:.2f}")

    if postcode:
        print(f"Postcode: {postcode}")

    if email:
        print(f"A receipt has been sent to {email} (imaginary mail server activated!)")

    print("-" * 60)
    print()

# -------------------------------
# Handle orders placed as BOXES
# -------------------------------
def handle_box_order(pizza_name, price):
    while True:
        qty_input = input("How many Box(es) do you want? (or type 'q' to cancel): ").strip()
        if qty_input.lower() == 'q':
            print('Box Order Cancelled')
            return
        elif qty_input.isdigit():
            quantity = int(qty_input)
            break
        else:
            print("Please enter a valid number.")

    # Ask if user wants a full meal (extras)
    extras_selected, extras_total = full_meal()

    # Apply discount if applicable
    discount_rate = 0.0
    if 5 <= quantity < 10:
        discount_rate = 0.10
    elif quantity >= 10:
        discount_rate = 0.20

    discount_applied = discount_rate > 0.0

    # Calculate total price
    sub_total = calculate_payment(price, quantity, discount_rate)
    total = sub_total + extras_total

    # Get delivery/takeout info
    delivery_type, address, postcode, email = handle_delivery_option()

    order_id = random.randint(1, 1000)  # Random order ID

    print(f"Your total payment is ${total:.2f} for {quantity} of {pizza_name} Pizza box(es) including selected extras.")
    if discount_applied:
        print(f"A discount of {int(discount_rate * 100)}% was applied.")

    # Show receipt
    generate_receipt(order_id, pizza_name, quantity, "Box", total, discount_applied, delivery_type, extras_selected, postcode, email, pizza_total=sub_total)

    # Save order to file
    save_order_to_json(pizza_name, "Box", quantity, total, discount_applied, extras_selected)

# -------------------------------
# Handle orders placed as SLICES
# -------------------------------
def handle_slice_order(pizza_name, slice_price):
    while True:
        qty_input = input("How many slices do you want? (or type 'q' to cancel): ").strip()
        if qty_input.lower() == 'q':
            print('Slice Order Cancelled')
            return
        elif qty_input.isdigit():
            quantity = int(qty_input)
            if quantity > 16:
                print("Maximum of 16 slices per order. Please try again.")
                continue
            break
        else:
            print("Please enter a valid number.")

    # Ask if user wants a full meal (extras)
    extras_selected, extras_total = full_meal()

    # Apply discount if 8 or more slices
    discount_rate = 0.05 if quantity >= 8 else 0.0
    discount_applied = discount_rate > 0.0

    # Calculate price and delivery
    sub_total = calculate_payment(slice_price, quantity, discount_rate)
    total = sub_total + extras_total
    delivery_type, address, postcode, email = handle_delivery_option()

    order_id = random.randint(1, 1000)

    print(f"Your total payment is ${total:.2f} for {quantity} of {pizza_name} Pizza Slice(s) including selected extras.")
    if discount_applied:
        print(f"A discount of {int(discount_rate * 100)}% was applied.")

    # Show receipt
    generate_receipt(order_id, pizza_name, quantity, "Slice", total, discount_applied, delivery_type, extras_selected, postcode, email, pizza_total=sub_total)

    # Save order
    save_order_to_json(pizza_name, "Slice", quantity, total, discount_applied, extras_selected)

# -------------------------------
# Handles user's pizza selection
# -------------------------------
def pizza_selection_order(pizza_type):
    if pizza_type in pizza_data:
        pizza = pizza_data[pizza_type]
        name = pizza["name"]
        price = pizza['price']
        slice_price = round(price / 8, 2)  # Estimate slice price

        print(f"You selected {name}\nPrice - ${price:.2f} per box | ${slice_price:.2f} per slice")

        while True:
            choice = input("Select 'B' for Box or 'S' for Slice (or 'q' to cancel): ").strip().upper()
            if choice == 'B':
                handle_box_order(name, price)
                break
            elif choice == 'S':
                handle_slice_order(name, slice_price)
                break
            elif choice == 'Q':
                print("Order Cancelled!")
                break
            else:
                print("Select either B, S or Q.")
    else:
        print("We do not have this Pizza Flavour for now. Maybe later!")

# -------------------------------
# Main Order System
# -------------------------------
def main_system():
    while True:
        print("\nWelcome to RushMore Pizzeria1\nTake a look at our Menu: ")
        for key, value in pizza_data.items():
            print(f"{key}: {value['name']} - ${value['price']:.2f}")

        print("Pick your choice from (1-9) and we serve you right away!\nor type in 'q' to quit:")
        choice = input("What do you want to pick? ").strip().lower()

        if choice == 'q':
            print("Goodbye and Have a nice day!\ntCome back another time...")
            break
        elif choice in pizza_data:
            pizza_selection_order(choice)
        else:
            print("Invalid Input, Please Try Again!")

# -------------------------------
# Entry Point of the Application
# -------------------------------
if __name__ == "__main__":
    main_system()  # Launch the pizza ordering system

