from products import Category,Product
import redis
import os

redis_client = redis.StrictRedis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)


def create_product(name, price, description, default_stock=10):
        product = Product(name, price, description, stock=default_stock)
        saved_stock = redis_client.get(f"stock:{name}")
        if saved_stock is not None:
            product.stock = int(saved_stock)
            product.active = product.stock > 0
        return product
    

class OrderSystem:
    def __init__(self):
        self.categories = {}
        self.populate_products()


    
    def set_stock(self, product_name, new_stock):
        for category in self.categories.values():
            for product in category.products:
                if not isinstance(product, Product):
                    continue
                if product.name.lower() == product_name.lower():
                    product.stock = new_stock
                    product.active = new_stock > 0
    
                    # ✅ Save to Redis
                    redis_client.set(f"stock:{product.name}", new_stock)
    
                    return f"✅ Stock for *{product.name}* set to {new_stock}."
        return f"❌ Product *{product_name}* not found."

    
    def populate_products(self):
        # Pantry
        pantry = Category("Pantry")
        pantry.add_product(create_product("Ace Instant Porridge 1kg Assorted", 27.99, "Instant porridge mix" ))
        pantry.add_product(create_product("All Gold Tomato Sauce 700g", 44.99, "Tomato sauce" ))
        pantry.add_product(create_product("Aromat Original 50g", 24.99, "Seasoning" ))
        pantry.add_product(create_product("Bakers Inn Bread", 23.99, "Brown loaf bread" ))
        pantry.add_product(create_product("Bakers Inn White Loaf", 23.99, "White loaf bread" ))
        pantry.add_product(create_product("Bella Macaroni 3kg", 82.99, "Macaroni pasta" ))
        pantry.add_product(create_product("Bisto Gravy 125g", 19.99, "Gravy mix" ))
        pantry.add_product(create_product("Blue Band Margarine 500g", 44.99, "Margarine" ))
        pantry.add_product(create_product("Blue Ribbon Self Raising 2kg", 37.99, "Self-raising flour" ))
        pantry.add_product(create_product("Bokomo Cornflakes 1kg", 54.90, "Cornflakes" ))
        pantry.add_product(create_product("Bullbrand Corned Beef 300g", 39.99, "Corned beef" ))
        pantry.add_product(create_product("Buttercup Margarine 500g", 44.99, "Margarine" ))
        pantry.add_product(create_product("Cashel Valley Baked Beans 400g", 18.99, "Baked beans" ))
        pantry.add_product(create_product("Cerevita 500g", 69.99, "Cereal" ))
        pantry.add_product(create_product("Cookmore Cooking Oil 2L", 67.99, "Cooking oil" ))
        pantry.add_product(create_product("Cross and Blackwell Mayonnaise 700g", 49.99, "Mayonnaise" ))
        pantry.add_product(create_product("Dried Kapenta 1kg", 134.99, "Dried fish" ))
        pantry.add_product(create_product("Ekonol Rice 5kg", 119.29, "Rice" ))
        pantry.add_product(create_product("Fattis Macaroni 500g", 22.99, "Macaroni" ))
        pantry.add_product(create_product("Gloria Self Raising Flour 5kg", 79.90, "Self-raising flour" ))
        pantry.add_product(create_product("Jungle Oats 1kg", 44.99, "Oats" ))
        pantry.add_product(create_product("Knorr Brown Onion Soup 50g", 7.99, "Onion soup mix" ))
        pantry.add_product(create_product("Lucky Star Pilchards in Tomato Sauce 155g", 17.99, "Pilchards" ))
        pantry.add_product(create_product("Mahatma Rice 2kg", 52.99, "Rice" ))
        pantry.add_product(create_product("Peanut Butter 350ml", 19.99, "Peanut butter" ))
        pantry.add_product(create_product("Roller Meal 10kg- Zim Meal", 136.99, "Maize meal" ))
        self.add_category(pantry)
                
        # Beverages
        beverages = Category("Beverages")
        beverages.add_product(create_product("Stella Teabags 100 Pack", 42.99, "Tea bags" ))
        beverages.add_product(create_product("Mazoe Raspberry 2 Litres", 67.99, "Fruit drink" ))
        beverages.add_product(create_product("Cremora Creamer 750g", 72.99, "Coffee creamer" ))
        beverages.add_product(create_product("Everyday Milk Powder 400g", 67.99, "Milk powder" ))
        beverages.add_product(create_product("Freshpack Rooibos 80s", 84.99, "Rooibos tea" ))
        beverages.add_product(create_product("Nestle Gold Cross Condensed Milk 385g", 29.99, "Condensed milk" ))
        beverages.add_product(create_product("Pine Nut Soft Drink 2L", 37.99, "Soft drink" ))
        beverages.add_product(create_product("Mazoe Blackberry 2L", 68.99, "Fruit drink" ))
        beverages.add_product(create_product("Quench Mango 2L", 32.99, "Fruit drink" ))
        beverages.add_product(create_product("Coca Cola 2L", 39.99, "Soft drink" ))
        beverages.add_product(create_product("Pfuko Dairibord Maheu 500ml", 14.99, "Maheu drink" ))
        beverages.add_product(create_product("Sprite 2 Litres", 37.99, "Soft drink" ))
        beverages.add_product(create_product("Pepsi (500ml x 24)", 178.99, "Soft drink pack" ))
        beverages.add_product(create_product("Probands Milk 500ml", 20.99, "Steri milk" ))
        beverages.add_product(create_product("Lyons Hot Chocolate 125g", 42.99, "Hot chocolate" ))
        beverages.add_product(create_product("Dendairy Long Life Full Cream Milk 1 Litre", 28.99, "Long life milk" ))
        beverages.add_product(create_product("Joko Tea Bags 100", 55.99, "Tea bags" ))
        beverages.add_product(create_product("Cool Splash 5 Litre Orange Juice", 99.99, "Orange juice" ))
        beverages.add_product(create_product("Cremora Coffee Creamer 750g", 72.99, "Coffee creamer" ))
        beverages.add_product(create_product("Fanta Orange 2 Litres", 37.99, "Soft drink" ))
        beverages.add_product(create_product("Quench Mango 5L", 92.25, "Fruit drink" ))
        beverages.add_product(create_product("Ricoffy Coffee 250g", 52.99, "Coffee" ))
        beverages.add_product(create_product("Dendairy Low Fat Long Life Milk", 28.99, "Low fat milk" ))
        beverages.add_product(create_product("Quickbrew Teabags 50", 25.99, "Teabags" ))
        beverages.add_product(create_product("Fruitrade 2L Orange Juice", 32.90, "Orange juice" ))
        beverages.add_product(create_product("Mazoe Orange Crush 2L", 69.99, "Fruit drink" ))
        beverages.add_product(create_product("Joko Rooibos Tea Bags 80s", 84.99, "Rooibos tea" ))
        self.add_category(beverages)
                
        # Household
        household = Category("Household")
        household.add_product(create_product("Sta Soft Lavender 2L", 59.99, "Fabric softener" ))
        household.add_product(create_product("Sunlight Dishwashing Liquid 750ml", 35.99, "Dishwashing liquid" ))
        household.add_product(create_product("Nova 2-Ply Toilet Paper 9s", 49.90, "Toilet paper" ))
        household.add_product(create_product("Domestos Thick Bleach Assorted 750ml", 39.99, "Bleach cleaner" ))
        household.add_product(create_product("Doom Odourless Multi-Insect Killer 300ml", 32.90, "Insect killer" ))
        household.add_product(create_product("Handy Andy Assorted 500ml", 32.99, "Multi-surface cleaner" ))
        household.add_product(create_product("Jik Assorted 750ml", 29.99, "Disinfectant" ))
        household.add_product(create_product("Maq Dishwashing Liquid 750ml", 35.99, "Dishwashing liquid" ))
        household.add_product(create_product("Maq 3kg Washing Powder", 72.90, "Washing powder" ))
        household.add_product(create_product("Maq Handwashing Powder 2kg", 78.99, "Handwashing powder" ))
        household.add_product(create_product("Elangeni Washing Bar 1kg", 24.59, "Washing bar" ))
        household.add_product(create_product("Vim Scourer 500g", 21.99, "Scouring pad" ))
        household.add_product(create_product("Matches Carton (10s)", 8.99, "Matches" ))
        household.add_product(create_product("Surf 5kg", 159.99, "Washing powder" ))
        household.add_product(create_product("Britelite Candles 6s", 32.99, "Candles" ))
        household.add_product(create_product("Sta-Soft Assorted Refill Sachet 2L", 39.99, "Fabric softener refill" ))
        household.add_product(create_product("Poppin Fresh Dishwashing Liquid 750ml", 22.99, "Dishwashing liquid" ))
        household.add_product(create_product("Poppin Fresh Toilet Cleaner 500ml", 34.99, "Toilet cleaner" ))
        household.add_product(create_product("Poppin Fresh Multi-Purpose Cleaner", 25.99, "Multi-purpose cleaner" ))
        self.add_category(household)
        
        # Personal Care
        personal_care = Category("Personal Care")
        personal_care.add_product(create_product("Softex Toilet Tissue 1-Ply 4s", 39.99, "Toilet tissue" ))
        personal_care.add_product(create_product("Protex Bath Soap Assorted 150g", 21.99, "Bath soap" ))
        personal_care.add_product(create_product("Sona Bath Soap 300g", 13.99, "Bath soap" ))
        personal_care.add_product(create_product("Kiwi Black Shoe Polish 50ml", 18.99, "Shoe polish" ))
        personal_care.add_product(create_product("Nivea Women's Roll On Assorted 50ml", 33.99, "Deodorant" ))
        personal_care.add_product(create_product("Clere Lanolin Lotion 400ml", 35.99, "Body lotion" ))
        personal_care.add_product(create_product("Vaseline Men Petroleum Jelly 250ml", 9.99, "Petroleum jelly" ))
        personal_care.add_product(create_product("Vaseline Petroleum Jelly Original 250ml", 39.99, "Petroleum jelly" ))
        personal_care.add_product(create_product("Sunlight Bath Soap Lively Lemon 175g", 10.90, "Bath soap" ))
        personal_care.add_product(create_product("Shield Fresh Shower Deo", 24.99, "Deodorant" ))
        personal_care.add_product(create_product("Hoity Toity Ladies Spray", 22.90, "Ladies spray" ))
        personal_care.add_product(create_product("Brut Total Attraction Roll On", 17.90, "Deodorant" ))
        personal_care.add_product(create_product("Vaseline Men Lotion 400ml", 64.99, "Body lotion" ))
        personal_care.add_product(create_product("Shield Dry Musk Roll On 50ml", 24.99, "Deodorant" ))
        personal_care.add_product(create_product("Sunlight Bath Soap Juicy Orange 150g", 10.99, "Bath soap" ))
        personal_care.add_product(create_product("Axe Men Roll On Wild Spice", 32.99, "Deodorant" ))
        personal_care.add_product(create_product("Nivea Rich Nourishing Cream 400ml", 79.99, "Body cream" ))
        personal_care.add_product(create_product("Dawn Rich Lanolin Lotion 400ml", 24.90, "Body lotion" ))
        personal_care.add_product(create_product("Twinsaver 2-Ply Toilet Paper", 32.90, "Toilet paper" ))
        personal_care.add_product(create_product("Hoity Toity Body Lotion 400ml", 44.90, "Body lotion" ))
        personal_care.add_product(create_product("Axe Deo Assorted Men", 36.99, "Deodorant" ))
        personal_care.add_product(create_product("Stayfree Pads Scented Wings 10s", 15.99, "Sanitary pads" ))
        personal_care.add_product(create_product("Geisha Bath Soap", 9.90, "Bath soap" ))
        personal_care.add_product(create_product("Clere Berries and Cream 500ml", 39.99, "Body lotion" ))
        personal_care.add_product(create_product("Clere Body Cream Cocoa Butter 500ml", 39.99, "Body cream" ))
        personal_care.add_product(create_product("Ingram's Camphor Cream Herbal 500ml", 57.99, "Herbal cream" ))
        personal_care.add_product(create_product("Lifebuoy Lemon Fresh 175g", 16.99, "Bath soap" ))
        personal_care.add_product(create_product("Aquafresh Fresh and Minty Toothpaste 100ml", 22.99, "Toothpaste" ))
        personal_care.add_product(create_product("Lil Lets Pads Super Maxi Thick 8s", 13.99, "Sanitary pads" ))
        personal_care.add_product(create_product("Nivea Men Lotion (Assorted) 400ml", 79.99, "Body lotion" ))
        personal_care.add_product(create_product("Nivea Men Cream (Assorted) 400ml", 79.99, "Body cream" ))
        personal_care.add_product(create_product("Nivea Body Creme Deep Impact 400ml", 79.99, "Body cream" ))
        personal_care.add_product(create_product("Clere Berries and Creme Lotion 400ml", 35.99, "Body lotion" ))
        personal_care.add_product(create_product("Clere Men 400ml Lotion Assorted", 35.99, "Men's lotion" ))
        personal_care.add_product(create_product("Pearl/Sona Bath Soap Assorted 200g", 13.99, "Bath soap" ))
        personal_care.add_product(create_product("Nivea Intensive Moisturizing Creme 500ml", 79.99, "Moisturizing cream" ))
        personal_care.add_product(create_product("Protex for Men Assorted Bath Soap 150g", 21.99, "Bath soap" ))
        personal_care.add_product(create_product("Axe Roll On Assorted", 36.99, "Deodorant" ))
        personal_care.add_product(create_product("Satiskin Floral Bouquet 2L", 99.99, "Body wash" ))
        personal_care.add_product(create_product("Nivea Deep Impact Lotion 400ml", 79.99, "Body lotion" ))
        personal_care.add_product(create_product("Nivea Ladies Deo Pearl Beauty", 32.90, "Deodorant" ))
        personal_care.add_product(create_product("Nivea Rich Nourishing Lotion 400ml", 79.99, "Body lotion" ))
        personal_care.add_product(create_product("Nivea Deo Dry Confidence Women 150ml", 32.99, "Deodorant" ))
        personal_care.add_product(create_product("Dove Roll On Assorted", 26.99, "Deodorant" ))
        personal_care.add_product(create_product("Satiskin Foam Bath Berry Fantasy 2L", 99.99, "Foam bath" ))
        personal_care.add_product(create_product("Clere Glycerin 100ml", 21.99, "Glycerin" ))
        personal_care.add_product(create_product("Nivea Body Creme Max Hydration 400ml", 79.99, "Body cream" ))
        personal_care.add_product(create_product("Clere Men Body Cream Assorted 400ml", 39.99, "Men's body cream" ))
        personal_care.add_product(create_product("Nivea Intensive Moisturizing Lotion 400g", 79.99, "Moisturizing lotion" ))
        personal_care.add_product(create_product("Lux Soft Touch 175g", 21.99, "Bath soap" ))
        personal_care.add_product(create_product("Lifebuoy Total 10 175g", 16.99, "Bath soap" ))
        personal_care.add_product(create_product("Jade Bath Soap Assorted", 12.60, "Bath soap" ))
        personal_care.add_product(create_product("Stayfree Pads Unscented Wings 10s", 19.90, "Sanitary pads" ))
        personal_care.add_product(create_product("Colgate 100ml", 18.99, "Toothpaste" ))
        personal_care.add_product(create_product("Clere Men Fire 450ml", 39.99, "Men's lotion" ))
        personal_care.add_product(create_product("Shield Men's Roll On Assorted", 24.99, "Deodorant" ))
        personal_care.add_product(create_product("Shower to Shower Ladies Deodorant", 27.99, "Deodorant" ))
        personal_care.add_product(create_product("Lux Soft Caress 175g", 21.99, "Bath soap" ))
        personal_care.add_product(create_product("Nivea Men Revitalizing Body Cream 400g", 79.99, "Body cream" ))
        personal_care.add_product(create_product("Clere Cocoa Butter Lotion 400ml", 32.99, "Body lotion" ))
        personal_care.add_product(create_product("Shield Women's Roll On Assorted", 24.99, "Deodorant" ))
        personal_care.add_product(create_product("Nivea All Season Body Lotion 400ml", 79.99, "Body lotion" ))
        personal_care.add_product(create_product("Nivea Men Roll On Assorted 50ml", 33.99, "Deodorant" ))
        personal_care.add_product(create_product("Protex Deep Clean Bath Soap 150g", 21.99, "Bath soap" ))
        personal_care.add_product(create_product("Sunlight Cooling Mint Bathing Soap 150g", 10.99, "Bath soap" ))
        personal_care.add_product(create_product("Dettol 250ml", 25.99, "Antiseptic liquid" ))
        personal_care.add_product(create_product("Woods Peppermint 100ml", 46.90, "Body spray" ))
        personal_care.add_product(create_product("Med Lemon Sachet 6.1g", 7.90, "Lemon sachet" ))
        personal_care.add_product(create_product("Predo Adult Diapers 30s (M/L/XL)", 317.99, "Adult diapers" ))
        personal_care.add_product(create_product("Ingram's Camphor Moisture Plus 500ml", 59.99, "Moisturizing cream" ))
        personal_care.add_product(create_product("Disposable Face Mask 50s", 39.99, "Face masks" ))
        self.add_category(personal_care)
        
        # Snacks and Sweets
        snacks = Category("Snacks and Sweets")        
        snacks.add_product(create_product("Jena Maputi 15pack", 23.99, "Popcorn" ))
        snacks.add_product(create_product("Tiggies Assorted 50s", 74.99, "Snacks" ))
        snacks.add_product(create_product("L Choice Assorted Biscuits", 12.90, "Biscuits" ))
        snacks.add_product(create_product("Sneaker Nax Bale Pack 2kg", 39.90, "Snacks" ))
        snacks.add_product(create_product("Yogueta Lollipop Split Pack 48 Pack", 59.99, "Lollipops" ))
        snacks.add_product(create_product("Arenel Choice Assorted Biscuits 150g", 19.90, "Biscuits" ))
        snacks.add_product(create_product("Willards Things 150g", 14.99, "Cheese snacks" ))
        snacks.add_product(create_product("Stumbo Assorted Lollipops 48s", 59.99, "Lollipops" ))
        snacks.add_product(create_product("Pringles Original 110g", 22.90, "Potato chips" ))
        snacks.add_product(create_product("Nibble Naks 20pack", 29.99, "Snacks" ))
        snacks.add_product(create_product("King Kurls Chicken Flavour 100g", 12.90, "Snacks" ))
        snacks.add_product(create_product("Nik Naks 50s Pack Assorted", 54.90, "Snacks" ))
        snacks.add_product(create_product("Proton Ramba Waraira Cookies 1kg", 68.99, "Cookies" ))
        snacks.add_product(create_product("Lobels Marie Biscuits", 6.90, "Biscuits" ))
        snacks.add_product(create_product("Chocolate Coated Biscuits", 35.99, "Chocolate biscuits" ))
        snacks.add_product(create_product("Top 10 Assorted Sweets", 9.90, "Assorted sweets" ))
        snacks.add_product(create_product("Jelido Magic Rings 102 Pieces", 48.90, "Candy rings" ))
        snacks.add_product(create_product("Lays Assorted Flavours 105g", 52.99, "Potato chips" ))
        snacks.add_product(create_product("Charhons Biscuits 2kg", 99.99, "Biscuits" ))
        snacks.add_product(create_product("Zap Nax Cheese and Onion 100g", 3.99, "Snacks" ))

        self.add_category(snacks)
        
        # Fresh Groceries
        fresh = Category("Fresh Groceries")       
        fresh.add_product(create_product("Economy Steak on Bone Beef Cuts 1kg", 147.99, "Fresh beef" ))
        fresh.add_product(create_product("Parmalat Cheddar Cheese", 89.99, "Cheddar cheese slices" ))
        fresh.add_product(create_product("Colcom Beef Polony 3kg", 299.00, "Beef polony" ))
        fresh.add_product(create_product("Colcom Tastee French Polony 750g", 116.99, "French polony" ))
        fresh.add_product(create_product("Colcom Chicken Polony 3kg", 219.90, "Chicken polony" ))
        fresh.add_product(create_product("Bulk Mixed Pork 1kg", 128.99, "Mixed pork" ))
        fresh.add_product(create_product("Potatoes 7.5kg (Small Pocket)", 219.99, "Fresh potatoes" ))
        fresh.add_product(create_product("Colcom Tastee Chicken Polony 1kg", 34.90, "Chicken polony" ))
        fresh.add_product(create_product("Colcom Garlic Polony 3kg", 220.00, "Garlic polony" ))
        fresh.add_product(create_product("Colcom Tastee Beef Polony 1kg", 35.00, "Beef polony" ))
        fresh.add_product(create_product("Wrapped Mixed Size Fresh Eggs 30", 149.99, "Fresh eggs" ))
        fresh.add_product(create_product("Texas Meats Juicy Boerewors", 159.99, "Boerewors" ))
        fresh.add_product(create_product("Unwrapped Small Size Fresh Eggs 30s", 99.99, "Fresh eggs" ))
        fresh.add_product(create_product("Irvines Mixed Chicken Cuts 2kg", 179.99, "Mixed chicken cuts" ))
        fresh.add_product(create_product("Dairibord Yoghurt 150ml", 15.99, "Yoghurt" ))
        self.add_category(fresh)
        
        # Stationery
        stationery = Category("Stationery")        
        stationery.add_product(create_product("Plastic Cover 3 Meter Roll", 7.99, "Plastic cover" ))
        stationery.add_product(create_product("Ruler 30cm", 6.99, "Ruler" ))
        stationery.add_product(create_product("A4 Bond Paper White", 126.99, "Bond paper" ))
        stationery.add_product(create_product("Kakhi Cover 3 Meter Roll", 8.99, "Kakhi cover" ))
        stationery.add_product(create_product("School Trunk", 750.00, "School trunk" ))
        stationery.add_product(create_product("Oxford Maths Set", 34.99, "Maths set" ))
        stationery.add_product(create_product("Grade 1-3 Exercise Book A4 32 Page (10 Pack)", 36.99, "Exercise books" ))
        stationery.add_product(create_product("72 Page Newsprint Maths Book (10 Pack)", 69.99, "Maths books" ))
        stationery.add_product(create_product("Cellotape Large 40yard", 5.99, "Cellotape" ))
        stationery.add_product(create_product("Newsprint 2 Quire Counter Books (192 Page)", 28.99, "Counter books" ))
        stationery.add_product(create_product("72 Page Newsprint Writing Exercise Book (10 Pack)", 69.99, "Writing exercise books" ))
        stationery.add_product(create_product("Cellotape Small 20yard", 3.99, "Cellotape" ))
        stationery.add_product(create_product("Eversharp Pens Set x 4", 14.99, "Pens set" ))
        stationery.add_product(create_product("Newsprint 1 Quire (96 Page) Counter Book", 17.99, "Counter book" ))
        stationery.add_product(create_product("HB Pencils x 12 Set", 24.99, "Pencils set" ))
        stationery.add_product(create_product("Sharp Scientific Calculator", 319.99, "Scientific calculator" ))
        stationery.add_product(create_product("32 Page Newsprint Plain Exercise Book (10 Pack)", 36.99, "Plain exercise books" ))
        self.add_category(stationery)
        
        # Baby Section
        baby_section = Category("Baby Section")        
        baby_section.add_product(create_product("Huggies Dry Comfort Jumbo Size 5 (44s)", 299.99, "Diapers" ))
        baby_section.add_product(create_product("Pampers Fresh Clean Wipes 64 Pack", 31.90, "Baby wipes" ))
        baby_section.add_product(create_product("Johnson and Johnson Scented Baby Jelly 325ml", 52.99, "Baby jelly" ))
        baby_section.add_product(create_product("Vaseline Baby Jelly 250g", 31.90, "Baby jelly" ))
        baby_section.add_product(create_product("Predo Baby Wipes Assorted 120s", 52.90, "Baby wipes" ))
        baby_section.add_product(create_product("Huggies Dry Comfort Size 3 Jumbo (76)", 299.99, "Diapers" ))
        baby_section.add_product(create_product("Huggies Dry Comfort Size 2 Jumbo (94)", 299.99, "Diapers" ))
        baby_section.add_product(create_product("Huggies Dry Comfort Size 4 Jumbo", 299.99, "Diapers" ))
        baby_section.add_product(create_product("Bennetts Aqueous Cream 500ml", 39.30, "Aqueous cream" ))
        baby_section.add_product(create_product("Predo Baby Wipes Assorted 80s", 38.99, "Baby wipes" ))
        baby_section.add_product(create_product("Crez Babyline Petroleum Jelly 500g", 42.99, "Petroleum jelly" ))
        baby_section.add_product(create_product("Johnson and Johnson Lightly Fragranced Aqueous Cream 350ml", 39.90, "Aqueous cream" ))
        baby_section.add_product(create_product("Nestle Baby Cereal with Milk Regular Wheat 250g", 34.99, "Baby cereal" ))
        baby_section.add_product(create_product("Nan 2: Infant Formula Optipro 400g", 79.99, "Infant formula" ))
        baby_section.add_product(create_product("Nan 1: Infant Formula Optipro 400g", 79.99, "Infant formula" ))
        self.add_category(baby_section)
        

    def add_category(self, category):
        self.categories[category.name] = category

    def list_categories(self):
        return list(self.categories.keys())

    def list_products(self, category_name):
        if category_name in self.categories:
            return [p for p in self.categories[category_name].products if p.is_available()]
        return []

    def get_all_products(self):
        all_products = []
        for cat in self.categories.values():
            all_products.extend(cat.products)
        return all_products

    def get_products_by_category(self):
            products_by_cat = {}
            for category in self.categories.values():
                product_lines = []
                # ✅ Filter only available products
                available_products = [p for p in category.products if p.is_available()]
                for i, product in enumerate(available_products, start=1):
                    line = f"{i}. {product.name} - R{product.price:.2f}"
                    product_lines.append(line)
                products_by_cat[category.name] = "\n".join(product_lines)
            return products_by_cat



    
    
