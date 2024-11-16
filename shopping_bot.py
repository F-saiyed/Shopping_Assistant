import openai
from product_data import PRODUCT_DB, RECOMMENDATIONS_DB
import re
import random
import os
from dotenv import load_dotenv
from difflib import get_close_matches
import uuid
from datetime import datetime

# Load the API key from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize shopping cart and conversation history
cart = []

class ShoppingAssistantBot:
    def __init__(self, model="gpt-4"):
        self.model = model
        self.current_step = "greeting"
        self.previous_step = None
        self.product_names = self.get_all_product_names()
        self.categories = list(PRODUCT_DB.keys())
        self.shipping_cost = 10.00  # Example flat shipping cost
        self.tax_rate = 0.07  # Example tax rate (7%)
        self.conversation_history = []  # Store conversation history for context-aware responses
        self.payment_info = {}  # Store payment and mailing info during checkout
        self.order_status = "No active orders"  # Placeholder for order status tracking
        self.context = {}  # Store details for multi-turn conversation context

    def get_all_product_names(self):
        all_products = []
        for category in PRODUCT_DB.values():
            all_products.extend(category.keys())
        return [product.lower().strip() for product in all_products]
    
    def generate_order_number(self):
        return uuid.uuid4().hex[:8].upper()


    def autocorrect(self, user_message):
        """Auto-correct words in the user's message based on product and category names."""
        words = user_message.split()
        corrected_words = []
        
        for word in words:
            # All words are handled in lowercase for case-insensitivity
            closest_match = get_close_matches(word.lower(), self.categories + self.product_names, n=1, cutoff=0.8)
            if closest_match:
                corrected_words.append(closest_match[0])
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)

    def get_categories(self):
        """Fetch and list all available product categories."""
        categories = list(PRODUCT_DB.keys())
        return f"We offer products in the following categories: {', '.join(categories)}."

    def get_product_info(self, product_name):
        """Fetch product information if available in the database."""
        for category, products in PRODUCT_DB.items():
            if product_name in products:
                product_info = products[product_name]
                return f"{product_name.capitalize()} details:\nPrice: ${product_info['price']}\nSpecifications: {product_info['specs']}\nAvailability: {product_info['availability']}."
        return f"Sorry, I couldn't find any information on {product_name}."

    def get_recommendations(self, product_name):
        """Suggest related or alternative products based on the user's query using local data."""
        if product_name in RECOMMENDATIONS_DB:
            recommendations = RECOMMENDATIONS_DB[product_name]
            return f"Here are some related products to consider: {', '.join(recommendations)}."
        
        for category, products in PRODUCT_DB.items():
            if product_name in products:
                other_products = [p for p in products.keys() if p != product_name]
                if other_products:
                    return f"You might also be interested in other {category} items: {', '.join(other_products)}."
                else:
                    return "No related products found."
        return "Sorry, I couldn't find recommendations for that product."
    
    def recommend_alternative_products(self, category):
        """Recommend products with 'In stock' or 'Limited stock' status from the same category."""
        recommendations = []
        for product, details in PRODUCT_DB[category].items():
            if details["availability"] in ["In stock", "Limited stock"]:
                recommendations.append(f"{product.capitalize()} ({details['availability']})")
        if recommendations:
            return f"Here are some alternative products available in the {category} category: {', '.join(recommendations)}."
        return "Unfortunately, no alternative products are available at the moment."
    
    def parse_add_to_cart_command(self, user_message):
        """Parse and normalize add-to-cart commands, handling special characters and different phrasing."""
        # Normalize the message by converting to lowercase and removing special characters
        cleaned_message = re.sub(r'[^a-zA-Z0-9\s]', '', user_message.lower().replace(" ", ""))

        # Look for common add-to-cart phrases
        if "add" in cleaned_message:
            items_to_add = re.split(r"and|,", cleaned_message)
            added_items = []

            for item in items_to_add:
                item = item.strip()  # Remove extra spaces
                exact_match_found = False

                # Normalize item name for matching
                normalized_item = item.replace(" ", "").replace("-", "").lower()

                # Check for exact or close match in the product database
                for category, products in PRODUCT_DB.items():
                    # Normalize product names in the database for matching
                    normalized_products = {name.replace(" ", "").replace("-", "").lower(): name for name in products.keys()}
                
                    # Exact match
                    if normalized_item in normalized_products:
                        product_name = normalized_products[normalized_item]
                        if products[product_name]["availability"] != "Out of stock":
                            self.add_to_cart(product_name)
                            added_items.append(product_name)
                        else:
                            recommendations = self.recommend_alternative_products(category)
                            return f"Sorry, {product_name} is out of stock. {recommendations}"
                        exact_match_found = True
                        break

                    # Close match
                    close_matches = get_close_matches(normalized_item, normalized_products.keys(), n=1, cutoff=0.6)
                    if close_matches:
                        closest_match = normalized_products[close_matches[0]]
                        if products[closest_match]["availability"] != "Out of stock":
                            self.add_to_cart(closest_match)
                            added_items.append(closest_match)
                        else:
                            recommendations = self.recommend_alternative_products(category)
                            return f"Sorry, {closest_match} is out of stock. {recommendations}"
                        exact_match_found = True
                        break

                if not exact_match_found:
                    return "Sorry, I couldn't identify the product(s) to add to your cart."

            if added_items:
                return f"Added {', '.join(added_items)} to your cart."
        return "Sorry, I couldn't identify the product(s) to add to your cart."

    def handle_message(self, user_message):
        # Convert the user message to lowercase to ensure case-insensitivity
        user_message = self.autocorrect(user_message.strip().lower())

        if user_message in ["how are you?", "how're you?", "how is your day?", "how are you doing?", "how’s your day?", "how's your day?"]:
            return "I'm doing well, thanks for asking! How can I assist you today?"

        shopping_phrases = ["shopping", "browsing", "i want to buy", "i am looking to buy something", "i want to do shopping","i want to shop","what do you have"]
        if any(phrase in user_message for phrase in shopping_phrases):
            return f"Great! You came to the right place. We have these categories of products: {self.get_categories()}"

        if self.is_greeting(user_message):
            return "Hello! How can I assist you today?"

        if self.is_interruption(user_message):
            return "The current task has been canceled. How else can I assist you?"
        
        if self.is_farewell(user_message):
            self.clear_cart()
            return "Thanks for chatting with me. Have a good day!"

        if "categories" in user_message or "what categories do you have" in user_message:
            return self.get_categories()
        
        # Route 'add' commands directly to parse_add_to_cart_command
        if "add" in user_message:
            response = self.parse_add_to_cart_command(user_message)
            if response:
                return response

        # Handle specific category inquiries
        for category in PRODUCT_DB:
            if category in user_message:
                return f"In our {category} category, we offer the following products: {', '.join(PRODUCT_DB[category].keys())}."
            
        #Check if the user input matches a product name directly to show product info
        cleaned_message = user_message.lower().strip()
        if cleaned_message in self.product_names:
            return self.get_product_info(cleaned_message)    

        if "checkout" in user_message:
            return self.checkout()

        if "delivery time" in user_message or "what's your delivery time" in user_message:
            return self.get_delivery_time()

        if "payment options" in user_message or "payment methods" in user_message:
            return self.get_payment_options()

        if "order status" in user_message:
            return self.get_order_status()

        # Process add-to-cart commands
        response = self.parse_add_to_cart_command(user_message)
        if response and "Sorry" not in response:
            return response

        if user_message in ["yes", "add it"]:
            product_name = self.context.get("last_product")
            if product_name:
                return self.add_to_cart(product_name)

        if "view cart" in user_message.lower() or "show cart" in user_message.lower():
            return self.view_cart()

        # Handle removing items from the cart with specific conditions
        if "remove" in user_message:
            if "last product" in user_message or "last product from cart" in user_message or "last item" in user_message:
                return self.remove_last_product_from_cart()
            elif "first product" in user_message or "first product from cart" in user_message or "first item" in user_message:
                return self.remove_first_product_from_cart()
            else:
                product_names = [product.strip() for product in user_message.replace("remove", "").replace("from cart", "").split(",")]
                responses = []
                for product_name in product_names:
                    if product_name in self.product_names:
                        responses.append(self.remove_from_cart(product_name))
                    else:
                        responses.append(f"Sorry, {product_name} is not in your cart or not recognized.")
                return "\n".join(responses)

        if "recommend" in user_message or "suggest" in user_message:
            product_name = next((product for product in self.product_names if product in user_message), None)
            if product_name:
                return self.get_recommendations(product_name)
            else:
                return "Please specify a product for recommendations."

        if any(product in user_message for product in self.product_names):
            product_name = next(product for product in self.product_names if product in user_message)
            return self.get_product_info(product_name)

        return self.get_gpt4_response(user_message)

    def get_gpt4_response(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.conversation_history,
                max_tokens=150,
                temperature=0.7
            )
            assistant_reply = response['choices'][0]['message']['content']
            self.conversation_history.append({"role": "assistant", "content": assistant_reply})
            return assistant_reply
        except Exception as e:
            return f"An error occurred while fetching the response: {e}"

    def is_greeting(self, message):
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon"]
        return any(greet in message for greet in greetings)

    def is_interruption(self, message):
        interruptions = ["stop", "cancel", "never mind"]
        return any(interrupt in message for interrupt in interruptions)
    
    def is_farewell(self, message):
        farewell = ["bye", "exit", "I don't need your help anymore"]
        return any(fare in message for fare in farewell)

    def add_to_cart(self, product_name, quantity=1):
        """Add a product to the cart, with out-of-stock handling and duplicate checking."""
        product = self.find_product_by_name(product_name)
        if product is None:
            return "Product not found. Please select from available items."
    
        # Check if the product is in stock
        if not product.get("availability", True):
            return f"Sorry, '{product_name}' is out of stock for now. Please select another item."
    
        # Check if the product already exists in the cart
        for item in cart:
            if item['product_name'] == product_name:
                item['quantity'] += quantity  # Update quantity
                return f"Updated quantity of {product_name} to {item['quantity']} in the cart."
    
        # If the product does not exist in the cart, add it as a new item
        item = {"product_name": product_name, "quantity": quantity}
        cart.append(item)
        return f"Added {quantity} of {product_name} to the cart."

    def view_cart(self):
        if not cart:
            return "Your cart is empty."
    
        cart_message = "\n".join([f"{item['quantity']} x {item['product_name']}" for item in cart])
        checkout_message = "\n\n-----\n\nIf you want to Checkout, please fill the required information in the Checkout box!"
    
        # Combine cart message and checkout message into one return value
        return f"{cart_message}{checkout_message}"


    def checkout(self, full_name, address, payment_method, card_number,cvv, expiry_date,email):
        """Process checkout by collecting user details, validating inputs, and calculating the final total."""
        if not cart:
            return "Your cart is empty. Add items before checking out."

        # Collect and validate full name
        if len(full_name) > 50:
            return "Full name is too long. Please enter a name with a maximum of 50 characters."
        
        # Collect and validate email
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return "Invalid email address. Please provide a valid email."

        # Collect and validate address
        if not re.match(r'^\d+\s+\w+\s+(street|st\.|Street|St\.|Road|Rd\.|Ave|Avenue|Drive|dr\.)$', address):
            return "Invalid address format. Please include 'Street', 'St.', 'Ave', or 'Avenue' in your address."

        # Collect and validate payment method
        if payment_method.lower() not in ["debit", "credit", "paypal"]:
            return "Invalid payment option. Please choose one of the provided option only!"
        
        # Remove any non-digit characters from the card number for validation
        card_number = re.sub(r'\D', '', card_number)  # This removes hyphens

        # Collect and validate card number
        if not card_number.isdigit() or len(card_number) != 16:
            return "Invalid card number. Please enter a 16-digit number."
        
        # Format card number to xxxx-xxxx-xxxx-xxxx
        formatted_card_number = f"{card_number[:4]}-{card_number[4:8]}-{card_number[8:12]}-{card_number[12:]}"

        # Collect and Validate CVV
        if not re.match(r'^\d{3}$', cvv):
            return "Invalid CVV. Please enter a 3-digit number."

        # Validate expiry date
        expiry_validation = self.validate_expiry_date(expiry_date)
        if expiry_validation:
            return expiry_validation

        # Store payment information after validation
        self.payment_info = {
        "full_name": full_name,
        "address": address,
        "email": email,
        "payment_method": payment_method,
        "card_number": formatted_card_number,
        "cvv": cvv,
        "expiry_date": expiry_date
        }

        # Calculate total cost from items in cart
        total_cost = 0.0
        for item in cart:
            product_info = self.find_product_by_name(item['product_name'])
            if product_info:
                price = float(product_info['price'].replace("$", ""))  # Convert price to float
                total_cost += price * item['quantity']
        tax = total_cost * self.tax_rate
        shipping = self.shipping_cost
        final_total = total_cost + tax + shipping
        order_number = self.generate_order_number()
        self.order_status = "Order placed, processing"
    
        return f"Total: ${final_total:.2f} (including tax and shipping). Thank you, {full_name}, for your order! Your order will be shipped to {address}.\n Order Number is {order_number}.\n A confirmation email has been sent to {email}."


    def validate_expiry_date(self,expiry_date):
        # Validate MM/YY format
        if not re.match(r'^(0[1-9]|1[0-2])/(\d{2})$', expiry_date):
            return "Invalid expiry date format. Please enter in MM/YY format."
    
        # Extract month and year from the input
        month, year = expiry_date.split('/')
        month = int(month)
        year = int(year) + 2000  # Convert YY to YYYY (e.g., 23 -> 2023)

        # Get current month and year
        today = datetime.today()
        current_year = today.year
        current_month = today.month

        # Check if the expiry date is in the current or future date
        if year < current_year or (year == current_year and month < current_month):
            return "Invalid expiry date. Please enter a current or future date."
    
        return None

    def get_delivery_time(self):
        return "Standard delivery time is 3-5 business days. Expedited options are available upon request."

    def get_payment_options(self):
        return "We accept debit and credit cards (Visa, MasterCard, and American Express) and PayPal."

    def get_order_status(self):
        return f"Your current order status: {self.order_status}"

    def set_payment_info(self, payment_method, address):
        self.payment_info["payment_method"] = payment_method
        self.payment_info["address"] = address
        return "Payment information and address saved. You can now proceed with checkout."

    def clear_cart(self):
        cart.clear()
        return "Your cart has been cleared."

    def remove_from_cart(self, product_name):
        for item in cart:
            if item['product_name'] == product_name:
                cart.remove(item)
                return f"{product_name} has been removed from your cart."
        return f"{product_name} is not in the cart."

    def remove_last_product_from_cart(self):
        """Removes the last added product from the cart."""
        if cart:
            last_product = cart.pop()  # Remove the last item
            return f"{last_product['product_name']} has been removed from your cart."
        return "Your cart is empty."

    def remove_first_product_from_cart(self):
        """Removes the first added product from the cart."""
        if cart:
            first_product = cart.pop(0)  # Remove the first item
            return f"{first_product['product_name']} has been removed from your cart."
        return "Your cart is empty."

    def update_quantity(self, product_name, quantity):
        for item in cart:
            if item['product_name'] == product_name:
                item['quantity'] = quantity
                return f"The quantity of {product_name} has been updated to {quantity}."
        return f"{product_name} is not in the cart."

    def find_product_by_name(self, product_name):
        """Helper function to locate a product by its name."""
        for category in PRODUCT_DB.values():
            if product_name in category:
                return category[product_name]
        return f"{product_name} is not in the Warehouse."