from flask import Flask, request, jsonify, render_template
from shopping_bot import ShoppingAssistantBot

# Initialize Flask app and chatbot instance
app = Flask(__name__)
bot = ShoppingAssistantBot()

@app.route('/')
def index():
    # Render the front-end HTML interface for the chatbot
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Receives user message, processes it, and returns bot response
    user_message = request.json.get("message")
    bot_response = bot.handle_message(user_message)
    return jsonify({"response": bot_response})

@app.route('/checkout', methods=['POST'])
def checkout():
    # Retrieve form data sent from the front end
    full_name = request.form.get('full_name')
    address = request.form.get('address')
    payment_method = request.form.get('payment_method')
    card_number = request.form.get('card_number')
    cvv = request.form.get('cvv')
    expiry_date = request.form.get('expiry_date')
    email = request.form.get('email')
    
    # Perform checkout using the ShoppingAssistantBot instance
    result = bot.checkout(full_name, address, payment_method, card_number,cvv, expiry_date,email)
    
    # Return the checkout result as a response
    return jsonify({"message": result})

if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)
