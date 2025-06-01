# MODIFIED WHATSAPP BOT CODE (with products listed instead of categories after name or "add item")

import os
import json
import requests
import redis

# --- ENVIRONMENT VARIABLES ---
WA_TOKEN = os.environ["WA_TOKEN"]
gen_api = os.environ.get("GEN_API")  # Gemini API Key
owner_phone = os.environ.get("OWNER_PHONE")


redis_client = Redis(
    url=os.environ["UPSTASH_REDIS_REST_URL"],
    token=os.environ["UPSTASH_REDIS_REST_TOKEN"]
)

SESSION_TIMEOUT_SECONDS = 60

# --- DATA STRUCTURES ---
CATEGORIES = [
    {
        "name": "Pantry",
        "products": [
            {"name": "Ace Instant Porridge 1kg Assorted", "price": 27.99, "desc": "Instant porridge mix"},
            {"name": "All Gold Tomato Sauce 700g", "price": 44.99, "desc": "Tomato sauce"},
            {"name": "Aromat Original 50g", "price": 24.99, "desc": "Seasoning"},
            {"name": "Bakers Inn Bread", "price": 23.99, "desc": "Brown loaf bread"},
            {"name": "Bakers Inn White Loaf", "price": 23.99, "desc": "White loaf bread"},
            {"name": "Bella Macaroni 3kg", "price": 82.99, "desc": "Macaroni pasta"},
            {"name": "Bisto Gravy 125g", "price": 19.99, "desc": "Gravy mix"},
            {"name": "Blue Band Margarine 500g", "price": 44.99, "desc": "Margarine"},
            {"name": "Blue Ribbon Self Raising 2kg", "price": 37.99, "desc": "Self-raising flour"},
            {"name": "Bokomo Cornflakes 1kg", "price": 54.90, "desc": "Cornflakes"},
            {"name": "Bullbrand Corned Beef 300g", "price": 39.99, "desc": "Corned beef"},
            {"name": "Buttercup Margarine 500g", "price": 44.99, "desc": "Margarine"},
            {"name": "Cashel Valley Baked Beans 400g", "price": 18.99, "desc": "Baked beans"},
            {"name": "Cerevita 500g", "price": 69.99, "desc": "Cereal"},
            {"name": "Cookmore Cooking Oil 2L", "price": 67.99, "desc": "Cooking oil"},
            {"name": "Cross and Blackwell Mayonnaise 700g", "price": 49.99, "desc": "Mayonnaise"},
            {"name": "Dried Kapenta 1kg", "price": 134.99, "desc": "Dried fish"},
            {"name": "Ekonol Rice 5kg", "price": 119.29, "desc": "Rice"},
            {"name": "Fattis Macaroni 500g", "price": 22.99, "desc": "Macaroni"},
            {"name": "Gloria Self Raising Flour 5kg", "price": 79.90, "desc": "Self-raising flour"},
            {"name": "Jungle Oats 1kg", "price": 44.99, "desc": "Oats"},
            {"name": "Knorr Brown Onion Soup 50g", "price": 7.99, "desc": "Onion soup mix"},
            {"name": "Lucky Star Pilchards in Tomato Sauce 155g", "price": 17.99, "desc": "Pilchards"},
            {"name": "Mahatma Rice 2kg", "price": 52.99, "desc": "Rice"},
            {"name": "Peanut Butter 350ml", "price": 19.99, "desc": "Peanut butter"},
            {"name": "Roller Meal 10kg- Zim Meal", "price": 136.99, "desc": "Maize meal"},
        ]
    },
    {
        "name": "Beverages",
        "products": [
            {"name": "Stella Teabags 100 Pack", "price": 42.99, "desc": "Tea bags"},
            {"name": "Mazoe Raspberry 2 Litres", "price": 67.99, "desc": "Fruit drink"},
            {"name": "Cremora Creamer 750g", "price": 72.99, "desc": "Coffee creamer"},
            {"name": "Everyday Milk Powder 400g", "price": 67.99, "desc": "Milk powder"},
            {"name": "Freshpack Rooibos 80s", "price": 84.99, "desc": "Rooibos tea"},
            {"name": "Nestle Gold Cross Condensed Milk 385g", "price": 29.99, "desc": "Condensed milk"},
            {"name": "Pine Nut Soft Drink 2L", "price": 37.99, "desc": "Soft drink"},
            {"name": "Mazoe Blackberry 2L", "price": 68.99, "desc": "Fruit drink"},
            {"name": "Quench Mango 2L", "price": 32.99, "desc": "Fruit drink"},
            {"name": "Coca Cola 2L", "price": 39.99, "desc": "Soft drink"},
            {"name": "Pfuko Dairibord Maheu 500ml", "price": 14.99, "desc": "Maheu drink"},
            {"name": "Sprite 2 Litres", "price": 37.99, "desc": "Soft drink"},
            {"name": "Pepsi (500ml x 24)", "price": 178.99, "desc": "Soft drink pack"},
            {"name": "Probands Milk 500ml", "price": 20.99, "desc": "Steri milk"},
            {"name": "Lyons Hot Chocolate 125g", "price": 42.99, "desc": "Hot chocolate"},
            {"name": "Dendairy Long Life Full Cream Milk 1 Litre", "price": 28.99, "desc": "Long life milk"},
            {"name": "Joko Tea Bags 100", "price": 55.99, "desc": "Tea bags"},
            {"name": "Cool Splash 5 Litre Orange Juice", "price": 99.99, "desc": "Orange juice"},
            {"name": "Cremora Coffee Creamer 750g", "price": 72.99, "desc": "Coffee creamer"},
            {"name": "Fanta Orange 2 Litres", "price": 37.99, "desc": "Soft drink"},
            {"name": "Quench Mango 5L", "price": 92.25, "desc": "Fruit drink"},
            {"name": "Ricoffy Coffee 250g", "price": 52.99, "desc": "Coffee"},
            {"name": "Dendairy Low Fat Long Life Milk", "price": 28.99, "desc": "Low fat milk"},
            {"name": "Quickbrew Teabags 50", "price": 25.99, "desc": "Teabags"},
            {"name": "Fruitrade 2L Orange Juice", "price": 32.90, "desc": "Orange juice"},
            {"name": "Mazoe Orange Crush 2L", "price": 69.99, "desc": "Fruit drink"},
            {"name": "Joko Rooibos Tea Bags 80s", "price": 84.99, "desc": "Rooibos tea"},
        ]
    },
    {
        "name": "Household",
        "products": [
            {"name": "Sta Soft Lavender 2L", "price": 59.99, "desc": "Fabric softener"},
            {"name": "Sunlight Dishwashing Liquid 750ml", "price": 35.99, "desc": "Dishwashing liquid"},
            {"name": "Nova 2-Ply Toilet Paper 9s", "price": 49.90, "desc": "Toilet paper"},
            {"name": "Domestos Thick Bleach Assorted 750ml", "price": 39.99, "desc": "Bleach cleaner"},
            {"name": "Doom Odourless Multi-Insect Killer 300ml", "price": 32.90, "desc": "Insect killer"},
            {"name": "Handy Andy Assorted 500ml", "price": 32.99, "desc": "Multi-surface cleaner"},
            {"name": "Jik Assorted 750ml", "price": 29.99, "desc": "Disinfectant"},
            {"name": "Maq Dishwashing Liquid 750ml", "price": 35.99, "desc": "Dishwashing liquid"},
            {"name": "Maq 3kg Washing Powder", "price": 72.90, "desc": "Washing powder"},
            {"name": "Maq Handwashing Powder 2kg", "price": 78.99, "desc": "Handwashing powder"},
            {"name": "Elangeni Washing Bar 1kg", "price": 24.59, "desc": "Washing bar"},
            {"name": "Vim Scourer 500g", "price": 21.99, "desc": "Scouring pad"},
            {"name": "Matches Carton (10s)", "price": 8.99, "desc": "Matches"},
            {"name": "Surf 5kg", "price": 159.99, "desc": "Washing powder"},
            {"name": "Britelite Candles 6s", "price": 32.99, "desc": "Candles"},
            {"name": "Sta-Soft Assorted Refill Sachet 2L", "price": 39.99, "desc": "Fabric softener refill"},
            {"name": "Poppin Fresh Dishwashing Liquid 750ml", "price": 22.99, "desc": "Dishwashing liquid"},
            {"name": "Poppin Fresh Toilet Cleaner 500ml", "price": 34.99, "desc": "Toilet cleaner"},
            {"name": "Poppin Fresh Multi-Purpose Cleaner", "price": 25.99, "desc": "Multi-purpose cleaner"},
        ]
    },
    # ... Add other categories from your main.py: Personal Care, Snacks and Sweets, Fresh Groceries, Stationery, Baby Section ...
]


# --- FLATTEN PRODUCTS ---
ALL_PRODUCTS = []
for category in CATEGORIES:
    for product in category['products']:
        ALL_PRODUCTS.append(product)

# --- UTILITY FUNCTIONS ---
def get_user_state(user_id):
    state = redis_client.get(f"user:{user_id}")
    if state:
        return json.loads(state)
    return {"step": "ask_name", "cart": [], "checkout": {}, "selected_product": None}

def save_user_state(user_id, state):
    redis_client.set(f"user:{user_id}", json.dumps(state), ex=60*60*3)

def send_whatsapp_message(text, to, phone_id):
    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    headers = {'Authorization': f'Bearer {WA_TOKEN}', 'Content-Type': 'application/json'}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    requests.post(url, headers=headers, json=data)

def list_all_products():
    return "\n".join([f"{i+1}. {p['name']} - R{p['price']:.2f}: {p['desc']}" for i, p in enumerate(ALL_PRODUCTS)])

def show_cart(cart):
    if not cart:
        return "Your cart is empty."
    lines = [f"{item['name']} x{item['qty']} = R{item['price']*item['qty']:.2f}" for item in cart]
    total = sum(item['price']*item['qty'] for item in cart)
    return "\n".join(lines) + f"\n\nTotal: R{total:.2f}"

# --- MAIN HANDLER ---
def handler(request, response):
    if request.method == "GET":
        mode = request.query.get("hub.mode")
        token = request.query.get("hub.verify_token")
        challenge = request.query.get("hub.challenge")
        if mode == "subscribe" and token == "BOT":
            response.status_code = 200
            response.body = challenge
            return response
        response.status_code = 403
        response.body = "Failed"
        return response

    if request.method == "POST":
        body = request.json()
        value = body["entry"][0]["changes"][0]["value"]
        if "messages" not in value or not value["messages"]:
            response.status_code = 200
            response.body = json.dumps({"status": "no user message"})
            return response

        data = value["messages"][0]
        phone_id = value["metadata"]["phone_number_id"]
        sender = data["from"]
        prompt = data["text"]["body"].strip()
        state = get_user_state(sender)

        step = state.get("step", "ask_name")
        cart = state.get("cart", [])

        if step == "ask_name":
            send_whatsapp_message("Hello! Welcome to Zimbogrocer. What's your name?", sender, phone_id)
            state["step"] = "save_name"

        elif step == "save_name":
            state["username"] = prompt.title()
            send_whatsapp_message(
                f"Thanks {state['username']}! Here's what we have in stock:\n{list_all_products()}\n\nSelect a product by number.",
                sender, phone_id
            )
            state["step"] = "choose_product"

        elif step == "choose_product":
            try:
                index = int(prompt) - 1
                if 0 <= index < len(ALL_PRODUCTS):
                    prod = ALL_PRODUCTS[index]
                    state["selected_product"] = prod
                    send_whatsapp_message(f"You selected {prod['name']}. How many would you like to add?", sender, phone_id)
                    state["step"] = "ask_quantity"
                else:
                    send_whatsapp_message("Invalid product number. Try again.", sender, phone_id)
            except:
                send_whatsapp_message("Please enter a valid product number.", sender, phone_id)

        elif step == "ask_quantity":
            try:
                qty = int(prompt)
                prod = state["selected_product"]
                if qty < 1:
                    raise ValueError
                cart.append({"name": prod["name"], "price": prod["price"], "qty": qty})
                state["cart"] = cart
                send_whatsapp_message(
                    "Item added to your cart.\nWhat would you like to do next?\n- View cart\n- Clear cart\n- Add Item",
                    sender, phone_id
                )
                state["step"] = "post_add_menu"
            except:
                send_whatsapp_message("Please enter a valid quantity.", sender, phone_id)

        elif step == "post_add_menu":
            if prompt.lower() == "view cart":
                send_whatsapp_message(show_cart(cart), sender, phone_id)
            elif prompt.lower() == "clear cart":
                cart.clear()
                state["cart"] = cart
                send_whatsapp_message("Cart cleared. What would you like to do next?\n- Add Item", sender, phone_id)
            elif prompt.lower() == "add item":
                send_whatsapp_message(f"Here's what we have in stock:\n{list_all_products()}\n\nSelect a product by number.", sender, phone_id)
                state["step"] = "choose_product"
            else:
                send_whatsapp_message("Invalid option. Please choose:\n- View cart\n- Clear cart\n- Add Item", sender, phone_id)

        save_user_state(sender, state)
        response.status_code = 200
        response.body = json.dumps({"status": "success"})
