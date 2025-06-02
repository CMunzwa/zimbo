import os
import logging
import requests
import random
import string
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
from orders import OrderSystem 
import traceback


logging.basicConfig(level=logging.INFO)

# Environment variables
wa_token = os.environ.get("WA_TOKEN")  # WhatsApp API Key
phone_id = os.environ.get("PHONE_ID") 

gen_api = os.environ.get("GEN_API")    # Gemini API Key
owner_phone = os.environ.get("OWNER_PHONE")
mongo_uri = os.environ.get("MONGO_URI", "mongodb+srv://admin:kuda123@cluster0.bkmbh.mongodb.net/")

# MongoDB setup
client = MongoClient(mongo_uri)
db = client.get_database("zim_grocery")
user_states_collection = db.user_states
orders_collection = db.orders

class User:
    def __init__(self, payer_name, payer_phone):
        self.payer_name = payer_name
        self.payer_phone = payer_phone
        self.cart = []
        self.checkout_data = {}
    
    def add_to_cart(self, product, quantity):
        # Check if product already in cart
        for item in self.cart:
            if item['product'].name == product.name:
                item['quantity'] += quantity
                return
        self.cart.append({"product": product, "quantity": quantity})
    
    def remove_from_cart(self, product_name):
        self.cart = [item for item in self.cart if item["product"].name.lower() != product_name.lower()]
    
    def clear_cart(self):
        self.cart = []
    
    def get_cart_contents(self):
        return [(item["product"], item["quantity"]) for item in self.cart]
    
    def get_cart_total(self):
        return sum(item["product"].price * item["quantity"] for item in self.cart)
    
    def to_dict(self):
        return {
            "payer_name": self.payer_name,
            "payer_phone": self.payer_phone,
            "cart": [{
                "product": {
                    "name": item["product"].name,
                    "price": item["product"].price,
                    "description": item["product"].description
                },
                "quantity": item["quantity"]
            } for item in self.cart],
            "checkout_data": self.checkout_data
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(data["payer_name"], data["payer_phone"])
        user.cart = [{
            "product": Product(
                item["product"]["name"],
                float(item["product"]["price"]),
                item["product"].get("description", "")
            ),
            "quantity": int(item["quantity"])
        } for item in data.get("cart", [])]
        user.checkout_data = data.get("checkout_data", {})
        return user

# State handlers
def handle_ask_name(prompt, user_data, phone_id):
    send("Hello! Welcome to Zimbogrocer. What's your name?", user_data['sender'], phone_id)
    update_user_state(user_data['sender'], {'step': 'save_name'})
    return {'step': 'save_name'}


def handle_save_name(prompt, user_data, phone_id):
    user = User(prompt.title(), user_data['sender'])
    
    # Create an instance of OrderSystem
    order_system = OrderSystem()
    
    # Get products by category
    categories_products = order_system.get_products_by_category()  # dict {category_name: products_str}
    
    category_names = list(categories_products.keys())
    current_index = 0
    first_category = category_names[current_index]
    first_products = categories_products[first_category]
    
    # Save user state with category index and product data
    update_user_state(user_data['sender'], {
        'step': 'choose_product',
        'user': user.to_dict(),
        'category_names': category_names,
        'current_category_index': current_index
    })
    
    message = (
        f"Thanks {user.payer_name}! Here are products from {first_category}:\n"
        f"{first_products}\n\nReply 'more' to see next category."
    )
    send(message, user_data['sender'], phone_id)
    
    return {'step': 'choose_product', 'user': user.to_dict()}


def handle_next_category(user_data, phone_id):
    state = get_user_state(user_data['sender'])
    category_names = state.get('category_names', [])
    current_index = state.get('current_category_index', 0)
    
    # Move to next category
    current_index += 1
    
    if current_index >= len(category_names):
        send(
            "No more categories. You can now select a product or type 'menu' to go back.",
            user_data['sender'], phone_id
        )
        return {'step': 'choose_product', 'user': state.get('user')}
    
    # Create instance of OrderSystem and fetch products again
    order_system = OrderSystem()
    categories_products = order_system.get_products_by_category()
    
    next_category = category_names[current_index]
    next_products = categories_products[next_category]
    
    # Update user state
    update_user_state(user_data['sender'], {
        'step': 'choose_product',
        'user': state.get('user'),
        'category_names': category_names,
        'current_category_index': current_index
    })
    
    message = (
        f"Here are products from {next_category}:\n"
        f"{next_products}\n\nReply 'more' to see next category."
    )
    send(message, user_data['sender'], phone_id)
    
    return {'step': 'choose_product', 'user': state.get('user')}



def handle_choose_category(prompt, user_data, phone_id):
    order_system = OrderSystem()
    if prompt.isalpha() and len(prompt) == 1:
        idx = ord(prompt.upper()) - 65
        categories = order_system.list_categories()
        if 0 <= idx < len(categories):
            cat = categories[idx]
            update_user_state(user_data['sender'], {
                'selected_category': cat,
                'step': 'choose_product'
            })
            send(f"Products in {cat}:\n{list_products(cat)}\nSelect a product by number.", user_data['sender'], phone_id)
            return {'step': 'choose_product', 'selected_category': cat}
        else:
            send("Invalid category. Try again:\n" + list_categories(), user_data['sender'], phone_id)
            return {'step': 'choose_category'}
    else:
        send("Please enter a valid category letter (e.g., A, B, C).", user_data['sender'], phone_id)
        return {'step': 'choose_category'}


def handle_choose_product(prompt, user_data, phone_id):
    try:
        index = int(prompt) - 1
        order_system = OrderSystem()
        products = order_system.get_all_products()
        if 0 <= index < len(products):
            selected_product = products[index]
            update_user_state(user_data['sender'], {
                'selected_product': {
                    'name': selected_product.name,
                    'price': selected_product.price,
                    'description': selected_product.description
                },
                'step': 'ask_quantity'
            })
            send(f"You selected {selected_product.name}. How many would you like to add?", user_data['sender'], phone_id)
            return {
                'step': 'ask_quantity',
                'selected_product': {
                    'name': selected_product.name,
                    'price': selected_product.price,
                    'description': selected_product.description
                }
            }
        else:
            send("Invalid product number. Try again.", user_data['sender'], phone_id)
            return {'step': 'choose_product'}
    except Exception:
        send("Please enter a valid product number.", user_data['sender'], phone_id)
        return {'step': 'choose_product'}



def handle_ask_quantity(prompt, user_data, phone_id):
    # Step 1: Try converting prompt to an integer
    try:
        print(f"[DEBUG] Raw user input: {prompt!r}")
        qty = int(prompt.strip())
        if qty < 1:
            raise ValueError("Quantity must be 1 or more.")
    except ValueError as ve:
        print(f"[ERROR] Invalid quantity input: {ve}")
        send("Please enter a valid number for quantity (e.g., 1, 2, 3).", user_data['sender'], phone_id)
        return {'step': 'ask_quantity', 'selected_product': user_data.get("selected_product", {})}

    # Step 2: Proceed with adding to cart
    try:
        user_dict = user_data.get('user')
        if not user_dict:
            raise KeyError("User data is missing.")

        selected_product_data = user_data.get("selected_product")
        if not selected_product_data:
            raise KeyError("Selected product data is missing.")

        user = User.from_dict(user_dict)
        selected_product = Product(
            selected_product_data['name'],
            selected_product_data['price'],
            selected_product_data.get('description', '')
        )

        user.add_to_cart(selected_product, qty)

        # Update state to post_add_menu
        update_user_state(user_data['sender'], {
            'user': user.to_dict(),
            'step': 'post_add_menu'
        })

        send(
            "Item added to your cart.\nWhat would you like to do next?\n"
            "- View cart\n- Clear cart\n- Remove <item>\n- Add Item",
            user_data['sender'],
            phone_id
        )

        return {
            'step': 'post_add_menu',
            'user': user.to_dict()
        }

    except Exception as e:
        print(f"[ERROR] Exception during cart update: {e}")
        traceback.print_exc()  # This gives you the exact error and line number
        send("Something went wrong while adding the item. Please try again.", user_data['sender'], phone_id)
        return {'step': 'ask_quantity', 'selected_product': user_data.get("selected_product", {})}


def handle_post_add_menu(prompt, user_data, phone_id):
    user = User.from_dict(user_data['user'])
    delivery_areas = {
        "Harare": 240,
        "Chitungwiza": 300,
        "Mabvuku": 300,
        "Ruwa": 300,
        "Domboshava": 250,
        "Southlea": 300,
        "Southview": 300,
        "Epworth": 300,
        "Mazoe": 300,
        "Chinhoyi": 350,
        "Banket": 350,
        "Rusape": 400,
        "Dema": 300
    }
    
    prompt = prompt.lower().strip()
    if prompt == "view cart":
        cart_message = show_cart(user)
        update_user_state(user_data['sender'], {
            'step': 'get_area',
            'delivery_areas': delivery_areas
        })
        send(cart_message + "\n\nPlease select your delivery area:\n" + list_delivery_areas(delivery_areas), user_data['sender'], phone_id)
        return {
            'step': 'get_area',
            'delivery_areas': delivery_areas,
            'user': user.to_dict()
        }
    elif prompt == "clear cart":
        user.clear_cart()
        update_user_state(user_data['sender'], {
            'user': user.to_dict(),
            'step': 'post_add_menu'
        })
        send("Cart cleared.\nWhat would you like to do next?\n- View cart\n- Add Item", user_data['sender'], phone_id)
        return {
            'step': 'post_add_menu',
            'user': user.to_dict()
        }
    elif prompt.startswith("remove "):
        item = prompt[7:].strip()
        user.remove_from_cart(item)
        update_user_state(user_data['sender'], {
            'user': user.to_dict(),
            'step': 'post_add_menu'
        })
        send(f"{item} removed from cart.\n{show_cart(user)}\nWhat would you like to do next?\n- View cart\n- Add Item", user_data['sender'], phone_id)
        return {
            'step': 'post_add_menu',
            'user': user.to_dict()
        }
    elif prompt in ["add", "add item", "add another", "add more"]:
        update_user_state(user_data['sender'], {'step': 'choose_category'})
        send("Sure! Here are the available products:\n" + list_all_products(), user_data['sender'], phone_id)
        return {'step': 'choose_product', 'user': user.to_dict()}

    else:
        send("Sorry, I didn't understand. You can:\n- View Cart\n- Clear Cart\n- Remove <item>\n- Add Item", user_data['sender'], phone_id)
        return {'step': 'post_add_menu', 'user': user.to_dict()}

def handle_get_area(prompt, user_data, phone_id):
    user = User.from_dict(user_data['user'])
    delivery_areas = user_data['delivery_areas']
    area = prompt.strip().title()
    
    if area in delivery_areas:
        user.checkout_data["delivery_area"] = area
        fee = delivery_areas[area]
        user.checkout_data["delivery_fee"] = fee
        delivery_product = Product(f"Delivery to {area}", fee, "Delivery fee")
        user.add_to_cart(delivery_product, 1)
        
        update_user_state(user_data['sender'], {
            'user': user.to_dict(),
            'step': 'ask_checkout'
        })
        
        send(f"{show_cart(user)}\nWould you like to checkout? (yes/no)", user_data['sender'], phone_id)
        return {
            'step': 'ask_checkout',
            'user': user.to_dict()
        }
    else:
        send(f"Invalid area. Please choose from:\n{list_delivery_areas(delivery_areas)}", user_data['sender'], phone_id)
        return {
            'step': 'get_area',
            'delivery_areas': delivery_areas,
            'user': user.to_dict()
        }

def handle_ask_checkout(prompt, user_data, phone_id):
    user = User.from_dict(user_data['user'])
    
    if prompt.lower() in ["yes", "y"]:
        update_user_state(user_data['sender'], {'step': 'get_receiver_name'})
        send("Please enter the receiver's full name.", user_data['sender'], phone_id)
        return {'step': 'get_receiver_name', 'user': user.to_dict()}
    elif prompt.lower() in ["no", "n"]:
        # Remove delivery fee if added
        user.remove_from_cart("Delivery to")
        update_user_state(user_data['sender'], {
            'user': user.to_dict(),
            'step': 'post_add_menu'
        })
        send("What would you like to do next?\n- View cart\n- Clear cart\n- Remove <item>\n- Add Item", user_data['sender'], phone_id)
        return {'step': 'post_add_menu', 'user': user.to_dict()}
    else:
        send("Please respond with 'yes' or 'no'.", user_data['sender'], phone_id)
        return {'step': 'ask_checkout', 'user': user.to_dict()}

def handle_get_receiver_name(prompt, user_data, phone_id):
    user = User.from_dict(user_data['user'])
    user.checkout_data["receiver_name"] = prompt
    update_user_state(user_data['sender'], {
        'user': user.to_dict(),
        'step': 'get_address'
    })
    send("Enter the delivery address.", user_data['sender'], phone_id)
    return {
        'step': 'get_address',
        'user': user.to_dict()
    }

def handle_get_address(prompt, user_data, phone_id):
    user = User.from_dict(user_data['user'])
    user.checkout_data["address"] = prompt
    update_user_state(user_data['sender'], {
        'user': user.to_dict(),
        'step': 'get_id'
    })
    send("Enter receiver's ID number.", user_data['sender'], phone_id)
    return {
        'step': 'get_id',
        'user': user.to_dict()
    }

def handle_get_id(prompt, user_data, phone_id):
    user = User.from_dict(user_data['user'])
    user.checkout_data["id_number"] = prompt
    update_user_state(user_data['sender'], {
        'user': user.to_dict(),
        'step': 'get_phone'
    })
    send("Enter receiver's phone number.", user_data['sender'], phone_id)
    return {
        'step': 'get_phone',
        'user': user.to_dict()
    }

def handle_get_phone(prompt, user_data, phone_id):
    user = User.from_dict(user_data['user'])
    user.checkout_data["phone"] = prompt
    details = user.checkout_data
    confirm_message = (
        f"Please confirm the details below:\n\n"
        f"Name: {details['receiver_name']}\n"
        f"Address: {details['address']}\n"
        f"ID: {details['id_number']}\n"
        f"Phone: {details['phone']}\n\n"
        "Are these correct? (yes/no)"
    )
    update_user_state(user_data['sender'], {
        'user': user.to_dict(),
        'step': 'confirm_details'
    })
    send(confirm_message, user_data['sender'], phone_id)
    return {
        'step': 'confirm_details',
        'user': user.to_dict()
    }

def handle_confirm_details(prompt, user_data, phone_id):
    user = User.from_dict(user_data['user'])
    
    if prompt.lower() in ["yes", "y"]:
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        payment_info = (
            f"Please make payment using one of the following options:\n\n"
            f"1. EFT\nBank: FNB\nName: Zimbogrocer (Pty) Ltd\nAccount: 62847698167\nBranch Code: 250655\nSwift Code: FIRNZAJJ\nReference: {order_id}\n"
            f"2. Pay at supermarkets: SHOPRITE, CHECKERS, USAVE, PICK N PAY, GAME, MAKRO or SPAR using Mukuru wicode\n\n"
            f"3. World Remit Transfer (payment details provided upon request)\n\n"
            f"4. Western Union (payment details provided upon request)\n\n"
            f"Order ID: {order_id}"
        )
        
        # Save order to database
        order_data = {
            'order_id': order_id,
            'user_data': user.to_dict(),
            'timestamp': datetime.now(),
            'status': 'pending',
            'total_amount': user.get_cart_total()
        }
        orders_collection.insert_one(order_data)
        
        # Notify owner
        owner_message = (
            f"New Order #{order_id}\n"
            f"From: {user.payer_name} ({user.payer_phone})\n"
            f"Receiver: {user.checkout_data['receiver_name']}\n"
            f"Address: {user.checkout_data['address']}\n"
            f"Phone: {user.checkout_data['phone']}\n"
            f"Items:\n{show_cart(user)}"
        )
        send(owner_message, owner_phone, phone_id)
        
        send(
            f"Order placed! 🛒\nOrder ID: {order_id}\n\n"
            f"{show_cart(user)}\n\n"
            f"Receiver: {user.checkout_data['receiver_name']}\n"
            f"Address: {user.checkout_data['address']}\n"
            f"Phone: {user.checkout_data['phone']}\n\n"
            f"{payment_info}\n\nWould you like to place another order? (yes/no)",
            user_data['sender'], phone_id
        )
        
        user.clear_cart()
        update_user_state(user_data['sender'], {
            'user': user.to_dict(),
            'step': 'ask_place_another_order'
        })
        
        return {
            'step': 'ask_place_another_order',
            'user': user.to_dict()
        }
    else:
        update_user_state(user_data['sender'], {
            'user': user.to_dict(),
            'step': 'get_receiver_name'
        })
        send("Okay, let's correct the details. What's the receiver's full name?", user_data['sender'], phone_id)
        return {
            'step': 'get_receiver_name',
            'user': user.to_dict()
        }

def handle_ask_place_another_order(prompt, user_data, phone_id):
    if prompt.lower() in ["yes", "y"]:
        update_user_state(user_data['sender'], {'step': 'choose_category'})
        send("Great! Please select a category:\n" + list_categories(), user_data['sender'], phone_id)
        return {'step': 'choose_category'}
    else:
        update_user_state(user_data['sender'], {'step': 'ask_name'})
        send("Thank you for shopping with us! Have a good day! 😊", user_data['sender'], phone_id)
        return {'step': 'ask_name'}

def handle_default(prompt, user_data, phone_id):
    send("Sorry, I didn't understand that. Please try again.", user_data['sender'], phone_id)
    return {'step': user_data.get('step', 'ask_name')}

# Utility functions
def get_user_state(phone_number):
    state = user_states_collection.find_one({'phone_number': phone_number})
    if state:
        state['_id'] = str(state['_id'])  # Convert ObjectId to string
        return state
    return {'step': 'ask_name', 'sender': phone_number}

def update_user_state(phone_number, updates):
    updates['phone_number'] = phone_number
    if 'sender' not in updates:
        updates['sender'] = phone_number
    user_states_collection.update_one(
        {'phone_number': phone_number},
        {'$set': updates},
        upsert=True
    )

def list_categories():
    order_system = OrderSystem()
    return "\n".join([f"{chr(65+i)}. {cat}" for i, cat in enumerate(order_system.list_categories())])

def list_products(category_name):
    order_system = OrderSystem()
    products = order_system.list_products(category_name)
    return "\n".join([f"{i+1}. {p.name} - R{p.price:.2f}" for i, p in enumerate(products)])

def show_cart(user):
    cart = user.get_cart_contents()
    if not cart:
        return "Your cart is empty."
    lines = [f"{p.name} x{q} = R{p.price*q:.2f}" for p, q in cart]
    total = sum(p.price*q for p, q in cart)
    return "\n".join(lines) + f"\n\nTotal: R{total:.2f}"

def list_delivery_areas(delivery_areas):
    return "\n".join([f"{k} - R{v:.2f}" for k, v in delivery_areas.items()])

def send(answer, sender, phone_id):
    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    headers = {
        'Authorization': f'Bearer {wa_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "to": sender,
        "type": "text",
        "text": {"body": answer}
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send message: {e}")

# Action mapping
action_mapping = {
    "ask_name": handle_ask_name,
    "save_name": handle_save_name,
    "choose_product": handle_choose_product,
    "ask_quantity": handle_ask_quantity,
    "post_add_menu": handle_post_add_menu,
    "get_area": handle_get_area,
    "ask_checkout": handle_ask_checkout,
    "get_receiver_name": handle_get_receiver_name,
    "get_address": handle_get_address,
    "get_id": handle_get_id,
    "get_phone": handle_get_phone,
    "confirm_details": handle_confirm_details,
    "ask_place_another_order": handle_ask_place_another_order,
}

def get_action(current_state, prompt, user_data, phone_id):
    handler = action_mapping.get(current_state, handle_default)
    return handler(prompt, user_data, phone_id)

# Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("connected.html")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == "BOT":  # Make sure this matches your WhatsApp Business API settings
            return challenge, 200
        return "Failed", 403

    elif request.method == "POST":
        data = request.get_json()
        logging.info(f"Incoming webhook data: {data}")  # Add logging
        
        try:
            # Extract message data
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            
            # Get phone_id from metadata
            phone_id = value["metadata"]["phone_number_id"]
            
            # Get message details
            messages = value.get("messages", [])
            if messages:
                message = messages[0]
                sender = message["from"]
                
                # Handle different message types
                if "text" in message:
                    prompt = message["text"]["body"].strip()
                    message_handler(prompt, sender, phone_id)
                else:
                    logging.info("Received non-text message")
                    send("Please send a text message", sender, phone_id)
                    
        except Exception as e:
            logging.error(f"Error processing webhook: {e}", exc_info=True)
            
        return jsonify({"status": "ok"}), 200

def list_all_products():
    order_system = OrderSystem()
    products = order_system.get_all_products()
    return "\n".join([f"{i+1}. {p.name} - R{p.price:.2f}" for i, p in enumerate(products)])


def message_handler(prompt, sender, phone_id):
    text = prompt.strip().lower()

    # Greeting triggers ask_name flow
    if text in ["hi", "hey", "hie"]:
        user_state = {'step': 'ask_name', 'sender': sender}
        updated_state = get_action('ask_name', prompt, user_state, phone_id)
        update_user_state(sender, updated_state)
        return

    # Load existing user state
    user_state = get_user_state(sender)
    user_state['sender'] = sender

    # Handle 'more' to show next category
    if text == "more" and user_state.get('step') == 'choose_product':
        updated_state = handle_next_category(user_state, phone_id)
        update_user_state(sender, updated_state)
        return

    # Default step handler
    updated_state = get_action(user_state['step'], prompt, user_state, phone_id)
    update_user_state(sender, updated_state)




if __name__ == "__main__":
    app.run(debug=True, port=8000)
