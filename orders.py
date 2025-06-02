from products import Category,Product

class OrderSystem:
    def __init__(self):
        self.categories = {}
        self.populate_products()

    def populate_products(self):
        # [TRUNCATED FOR BREVITY - assume entire product population code provided by user here]
        pass  # placeholder for actual content from user

    def add_category(self, category):
        self.categories[category.name] = category

    def list_categories(self):
        return list(self.categories.keys())

    def list_products(self, category_name):
        return self.categories[category_name].products if category_name in self.categories else []

    def get_all_products(self):
        all_products = []
        for cat in self.categories.values():
            all_products.extend(cat.products)
        return all_products
