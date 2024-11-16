# product_data.py

# Product database with specified portfolios
PRODUCT_DB = {
    "electronics": {
        "laptop": {"specs": "Intel i5, 8GB RAM, 256GB SSD", "price": "$700", "availability": "In stock"},
        "smartwatch": {"specs": "Heart-rate monitoring, GPS, Waterproof", "price": "$150", "availability": "Limited stock"},
        "headphones": {"specs": "Wireless, Noise-canceling", "price": "$120", "availability": "Out of stock"},
    },
    "home_appliances": {
        "vacuum cleaner": {"specs": "Bagless, 2000W", "price": "$180", "availability": "In stock"},
        "air purifier": {"specs": "HEPA filter, covers 400 sq ft", "price": "$250", "availability": "Limited stock"},
        "microwave": {"specs": "1200W, 1.2 cu ft", "price": "$200", "availability": "Out of stock"},
    },
    "apparel": {
        "jeans": {"specs": "Denim, various sizes", "price": "$40", "availability": "Limited stock"},
        "track pants": {"specs": "Cargo, various sizes", "price": "$40", "availability": "Limited stock"},
        "jacket": {"specs": "Waterproof, various sizes", "price": "$60", "availability": "Out of stock"},
    },
    "beauty_and_health": {
        "face cream": {"specs": "Moisturizing, SPF 30", "price": "$25", "availability": "In stock"},
        "shampoo": {"specs": "Sulfate-free, 500ml", "price": "$15", "availability": "Out of stock"},
        "lipstick": {"specs": "Matte finish, various shades", "price": "$10", "availability": "Limited stock"},
    },
    "groceries": {
        "rice": {"specs": "5kg bag", "price": "$10", "availability": "In stock"},
        "pasta": {"specs": "1kg pack", "price": "$5", "availability": "Out of stock"},
        "olive oil": {"specs": "500ml bottle", "price": "$8", "availability": "Limited stock"},
    },
}

# Recommendations for related products
RECOMMENDATIONS_DB = {
    "laptop": ["Gaming Laptop", "Ultrabook", "2-in-1 Laptop"],
    "smartwatch": ["Fitness Tracker", "Luxury Watch"],
    "headphones": ["Earbuds", "Over-ear Headphones"],
    "t-shirt": ["Sweater", "Hoodie"],
    "face cream": ["Sunscreen", "Body Lotion"],
    "rice": ["Quinoa", "Oats"],
    # Add additional recommendations as needed
}
