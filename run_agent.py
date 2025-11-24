"""
Manual Agent Runner
Run the Product Search Agent interactively from command line.
"""
import asyncio
import json
import sys
import logging
import aiohttp
from agents import ProductSearchAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_fallback_products():
    """Return a comprehensive list of 50+ sample products with all details."""
    return [
        {"name": "Wireless Bluetooth Headphones", "category": "electronics", "price": 79.99, "retailer": "FakeStore"},
        {"name": "Smartphone 128GB", "category": "electronics", "price": 599.99, "retailer": "DummyJSON"},
        {"name": "Laptop 15.6 inch", "category": "electronics", "price": 899.99, "retailer": "FakeStore"},
        {"name": "Wireless Mouse", "category": "electronics", "price": 29.99, "retailer": "DummyJSON"},
        {"name": "Mechanical Keyboard", "category": "electronics", "price": 129.99, "retailer": "FakeStore"},
        {"name": "4K Monitor 27 inch", "category": "electronics", "price": 349.99, "retailer": "DummyJSON"},
        {"name": "USB-C Hub", "category": "electronics", "price": 49.99, "retailer": "FakeStore"},
        {"name": "Webcam HD 1080p", "category": "electronics", "price": 69.99, "retailer": "DummyJSON"},
        {"name": "Tablet 10 inch", "category": "electronics", "price": 299.99, "retailer": "FakeStore"},
        {"name": "Smart Watch", "category": "electronics", "price": 199.99, "retailer": "DummyJSON"},
        {"name": "Gaming Chair", "category": "furniture", "price": 249.99, "retailer": "FakeStore"},
        {"name": "Standing Desk", "category": "furniture", "price": 399.99, "retailer": "DummyJSON"},
        {"name": "Office Chair Ergonomic", "category": "furniture", "price": 179.99, "retailer": "FakeStore"},
        {"name": "Desk Lamp LED", "category": "furniture", "price": 39.99, "retailer": "DummyJSON"},
        {"name": "Bookshelf 5 Tier", "category": "furniture", "price": 89.99, "retailer": "FakeStore"},
        {"name": "Coffee Table Glass", "category": "furniture", "price": 149.99, "retailer": "DummyJSON"},
        {"name": "Sofa 3 Seater", "category": "furniture", "price": 599.99, "retailer": "FakeStore"},
        {"name": "Dining Table Set", "category": "furniture", "price": 449.99, "retailer": "DummyJSON"},
        {"name": "Bed Frame Queen", "category": "furniture", "price": 299.99, "retailer": "FakeStore"},
        {"name": "Wardrobe 4 Door", "category": "furniture", "price": 399.99, "retailer": "DummyJSON"},
        {"name": "Cotton T-Shirt", "category": "clothing", "price": 19.99, "retailer": "FakeStore"},
        {"name": "Denim Jeans", "category": "clothing", "price": 49.99, "retailer": "DummyJSON"},
        {"name": "Hoodie Pullover", "category": "clothing", "price": 39.99, "retailer": "FakeStore"},
        {"name": "Running Shoes", "category": "clothing", "price": 89.99, "retailer": "DummyJSON"},
        {"name": "Winter Jacket", "category": "clothing", "price": 129.99, "retailer": "FakeStore"},
        {"name": "Sunglasses Aviator", "category": "clothing", "price": 59.99, "retailer": "DummyJSON"},
        {"name": "Backpack Laptop", "category": "clothing", "price": 69.99, "retailer": "FakeStore"},
        {"name": "Leather Belt", "category": "clothing", "price": 29.99, "retailer": "DummyJSON"},
        {"name": "Baseball Cap", "category": "clothing", "price": 24.99, "retailer": "FakeStore"},
        {"name": "Wristwatch Classic", "category": "clothing", "price": 149.99, "retailer": "DummyJSON"},
        {"name": "Coffee Maker", "category": "home", "price": 79.99, "retailer": "FakeStore"},
        {"name": "Air Fryer 5QT", "category": "home", "price": 99.99, "retailer": "DummyJSON"},
        {"name": "Blender Professional", "category": "home", "price": 129.99, "retailer": "FakeStore"},
        {"name": "Microwave Oven", "category": "home", "price": 149.99, "retailer": "DummyJSON"},
        {"name": "Toaster 4 Slice", "category": "home", "price": 49.99, "retailer": "FakeStore"},
        {"name": "Rice Cooker", "category": "home", "price": 59.99, "retailer": "DummyJSON"},
        {"name": "Vacuum Cleaner", "category": "home", "price": 199.99, "retailer": "FakeStore"},
        {"name": "Robot Vacuum", "category": "home", "price": 299.99, "retailer": "DummyJSON"},
        {"name": "Air Purifier HEPA", "category": "home", "price": 179.99, "retailer": "FakeStore"},
        {"name": "Humidifier Ultrasonic", "category": "home", "price": 69.99, "retailer": "DummyJSON"},
        {"name": "Action Camera 4K", "category": "electronics", "price": 199.99, "retailer": "FakeStore"},
        {"name": "Drone with Camera", "category": "electronics", "price": 449.99, "retailer": "DummyJSON"},
        {"name": "Portable Speaker", "category": "electronics", "price": 79.99, "retailer": "FakeStore"},
        {"name": "Earbuds Wireless", "category": "electronics", "price": 99.99, "retailer": "DummyJSON"},
        {"name": "Power Bank 20000mAh", "category": "electronics", "price": 39.99, "retailer": "FakeStore"},
        {"name": "Phone Case Protective", "category": "electronics", "price": 19.99, "retailer": "DummyJSON"},
        {"name": "Screen Protector Glass", "category": "electronics", "price": 14.99, "retailer": "FakeStore"},
        {"name": "Laptop Stand Aluminum", "category": "electronics", "price": 49.99, "retailer": "DummyJSON"},
        {"name": "External Hard Drive 2TB", "category": "electronics", "price": 89.99, "retailer": "FakeStore"},
        {"name": "USB Flash Drive 128GB", "category": "electronics", "price": 24.99, "retailer": "DummyJSON"},
        {"name": "Yoga Mat Premium", "category": "sports", "price": 34.99, "retailer": "FakeStore"},
        {"name": "Dumbbells Set 20kg", "category": "sports", "price": 79.99, "retailer": "DummyJSON"},
        {"name": "Bicycle Helmet", "category": "sports", "price": 49.99, "retailer": "FakeStore"},
        {"name": "Tennis Racket", "category": "sports", "price": 89.99, "retailer": "DummyJSON"},
        {"name": "Basketball Official", "category": "sports", "price": 29.99, "retailer": "FakeStore"},
        {"name": "Fitness Tracker", "category": "sports", "price": 59.99, "retailer": "DummyJSON"},
        {"name": "Resistance Bands Set", "category": "sports", "price": 24.99, "retailer": "FakeStore"},
        {"name": "Jump Rope", "category": "sports", "price": 14.99, "retailer": "DummyJSON"},
        {"name": "Water Bottle Insulated", "category": "sports", "price": 29.99, "retailer": "FakeStore"},
        {"name": "Gym Bag Large", "category": "sports", "price": 39.99, "retailer": "DummyJSON"},
        {"name": "Protein Shaker Bottle", "category": "sports", "price": 19.99, "retailer": "FakeStore"},
    ]

async def fetch_sample_products():
    """Fetch sample products from APIs to show what's available."""
    sample_products = []
    categories = set()
    api_success = False
    
    try:
        # Fetch from FakeStore API
        async with aiohttp.ClientSession() as session:
            async with session.get("https://fakestoreapi.com/products", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    fakestore_data = await response.json()
                    if isinstance(fakestore_data, list) and len(fakestore_data) > 0:
                        api_success = True
                        for item in fakestore_data[:15]:  # Get first 15 products
                            sample_products.append({
                                "name": item.get("title", "Unknown"),
                                "category": item.get("category", ""),
                                "price": item.get("price", 0),
                                "retailer": "FakeStore"
                            })
                            if item.get("category"):
                                categories.add(item.get("category"))
    except Exception as e:
        logging.debug(f"Could not fetch FakeStore samples: {e}")
    
    try:
        # Fetch from DummyJSON API
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dummyjson.com/products?limit=15", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    dummyjson_data = await response.json()
                    products = dummyjson_data.get("products", [])
                    if isinstance(products, list) and len(products) > 0:
                        api_success = True
                        for item in products[:15]:  # Get first 15 products
                            sample_products.append({
                                "name": item.get("title", "Unknown"),
                                "category": item.get("category", ""),
                                "price": item.get("price", 0),
                                "retailer": "DummyJSON"
                            })
                            if item.get("category"):
                                categories.add(item.get("category"))
    except Exception as e:
        logging.debug(f"Could not fetch DummyJSON samples: {e}")
    
    # If API calls failed or returned no products, use fallback
    if not api_success or len(sample_products) == 0:
        sample_products = get_fallback_products()
        # Extract categories from fallback products
        categories = set(p["category"] for p in sample_products if p.get("category"))
    
    return sample_products, sorted(categories)

def print_sample_products(sample_products, categories):
    """Display sample products and categories to help users understand what's available."""
    print("\n" + "="*60)
    print("Available Products & Categories")
    print("="*60)
    
    if categories:
        print("\nAvailable Categories:")
        for i, category in enumerate(categories, 1):
            print(f"   {i}. {category.title()}")
    
    if sample_products:
        print(f"\nSample Products ({len(sample_products)} available):")
        # Show all products, but group them for better readability
        for i, product in enumerate(sample_products, 1):
            category_str = f" ({product['category']})" if product.get('category') else ""
            price_str = f"${product['price']:.2f}" if product.get('price') else "N/A"
            retailer_str = f"[{product['retailer']}]" if product.get('retailer') else ""
            print(f"   {i:2d}. {product['name']}{category_str} - {price_str} {retailer_str}")
    
    print(f"\nTip: You can search by product name, category, or any keyword")
    print(f"Total: {len(sample_products)} products available across {len(categories)} categories")
    print("="*60)

def print_products(products, max_display=10):
    """Pretty print products."""
    if not products:
        print("   No products found.")
        return
    
    print(f"\n   Found {len(products)} products:\n")
    for i, product in enumerate(products[:max_display], 1):
        print(f"   {i}. {product['name']}")
        print(f"      Retailer: {product['retailer']}")
        print(f"      Price: ${product['price']:.2f}")
        if product.get('shipping_cost', 0) > 0:
            print(f"      Shipping: ${product['shipping_cost']:.2f}")
        print(f"      Total: ${product['total_price']:.2f}")
        if product.get('rating'):
            print(f"      Rating: {product['rating']}/5.0 ({product.get('review_count', 0)} reviews)")
        if product.get('url'):
            print(f"      URL: {product['url']}")
        print()

async def run_search(search_term, max_results=5, platforms=None, min_price=None, max_price=None):
    """Run a product search."""
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Warning: config.json not found. Using default configuration.")
        config = {}
    
    # Initialize agent
    agent_config = config.get("agents", {}).get("product_search", {})
    agent = ProductSearchAgent(agent_config)
    
    # Build query
    query = {
        "search_term": search_term,
        "max_results": max_results,
        "platforms": platforms or ["fakestore", "dummyjson"]
    }
    
    # Add filters if provided
    filters = {}
    if min_price is not None:
        filters["min_price"] = min_price
    if max_price is not None:
        filters["max_price"] = max_price
    if filters:
        query["filters"] = filters
    
    print(f"\nSearching for: '{search_term}'")
    if filters:
        print(f"Price filters: {filters}")
    print(f"Max results: {max_results}")
    print(f"Platforms: {', '.join(query['platforms'])}")
    print("\n" + "="*60)
    
    # Execute search
    result = await agent.execute(query)
    
    # Display results
    print(f"\nSearch Status: {'Success' if result['success'] else 'Failed'}")
    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return
    
    print(f"Total Results: {result['total_results']}")
    print(f"Platforms Searched: {', '.join(result['platforms_searched'])}")
    
    if result['products']:
        print_products(result['products'], max_display=max_results)
    else:
        print("\n   No products found.")
    
    print("="*60)

def main():
    """Main function for command-line interface."""
    print("\n" + "="*60)
    print("Product Search Agent - Manual Runner")
    print("="*60)
    
    if len(sys.argv) < 2:
        # Interactive mode
        print("\nInteractive Mode")
        print("   (Or use: python run_agent.py 'search term' [options])\n")
        
        # Fetch and display sample products
        print("Loading available products...")
        try:
            sample_products, categories = asyncio.run(fetch_sample_products())
            print_sample_products(sample_products, categories)
        except Exception as e:
            logging.debug(f"Could not load sample products: {e}")
            print("\nTip: You can search for products like 'laptop', 'phone', 'headphones', etc.")
        
        print()
        search_term = input("Enter search term: ").strip()
        if not search_term:
            print("Error: Search term cannot be empty!")
            return
        
        max_results_input = input("Max results (default 5): ").strip()
        max_results = int(max_results_input) if max_results_input.isdigit() else 5
        
        print("\nAvailable platforms:")
        print("   - fakestore, dummyjson (no API keys needed, default)")
        print("   - ebay, amazon (require API keys)")
        platforms_input = input("Platforms (comma-separated, or 'all' for fakestore+dummyjson, default 'all'): ").strip().lower()
        if platforms_input == 'all' or not platforms_input:
            platforms = ["fakestore", "dummyjson"]
        else:
            platforms = [p.strip() for p in platforms_input.split(',')]
        
        min_price_input = input("Min price (optional, press Enter to skip): ").strip()
        min_price = float(min_price_input) if min_price_input and min_price_input.replace('.', '').isdigit() else None
        
        max_price_input = input("Max price (optional, press Enter to skip): ").strip()
        max_price = float(max_price_input) if max_price_input and max_price_input.replace('.', '').isdigit() else None
        
        asyncio.run(run_search(search_term, max_results, platforms, min_price, max_price))
        
    else:
        # Command-line mode
        search_term = sys.argv[1]
        max_results = 5
        platforms = ["fakestore", "dummyjson"]
        min_price = None
        max_price = None
        
        # Parse optional arguments
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == "--max-results" and i + 1 < len(sys.argv):
                max_results = int(sys.argv[i + 1])
                i += 2
            elif arg == "--platforms" and i + 1 < len(sys.argv):
                platforms = [p.strip() for p in sys.argv[i + 1].split(',')]
                i += 2
            elif arg == "--min-price" and i + 1 < len(sys.argv):
                min_price = float(sys.argv[i + 1])
                i += 2
            elif arg == "--max-price" and i + 1 < len(sys.argv):
                max_price = float(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        asyncio.run(run_search(search_term, max_results, platforms, min_price, max_price))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

