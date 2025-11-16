"""
Manual Agent Runner
Run the Product Search Agent interactively from command line.
"""
import asyncio
import json
import sys
import logging
from agents import ProductSearchAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
        print("⚠️  config.json not found. Using default configuration.")
        config = {}
    
    # Initialize agent
    agent_config = config.get("agents", {}).get("product_search", {})
    agent = ProductSearchAgent(agent_config)
    
    # Build query
    query = {
        "search_term": search_term,
        "max_results": max_results,
        "platforms": platforms or ["ebay", "amazon"]
    }
    
    # Add filters if provided
    filters = {}
    if min_price is not None:
        filters["min_price"] = min_price
    if max_price is not None:
        filters["max_price"] = max_price
    if filters:
        query["filters"] = filters
    
    print(f"\n🔍 Searching for: '{search_term}'")
    if filters:
        print(f"💰 Filters: {filters}")
    print(f"📦 Max results: {max_results}")
    print(f"🛒 Platforms: {', '.join(query['platforms'])}")
    print("\n" + "="*60)
    
    # Execute search
    result = await agent.execute(query)
    
    # Display results
    print(f"\n✅ Search Status: {'Success' if result['success'] else 'Failed'}")
    if not result['success']:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    print(f"📊 Total Results: {result['total_results']}")
    print(f"🛒 Platforms Searched: {', '.join(result['platforms_searched'])}")
    
    if result['products']:
        print_products(result['products'], max_display=max_results)
    else:
        print("\n   No products found.")
    
    print("="*60)

def main():
    """Main function for command-line interface."""
    print("\n" + "="*60)
    print("🛍️  Product Search Agent - Manual Runner")
    print("="*60)
    
    if len(sys.argv) < 2:
        # Interactive mode
        print("\n📝 Interactive Mode")
        print("   (Or use: python run_agent.py 'search term' [options])\n")
        
        search_term = input("Enter search term: ").strip()
        if not search_term:
            print("❌ Search term cannot be empty!")
            return
        
        max_results_input = input("Max results (default 5): ").strip()
        max_results = int(max_results_input) if max_results_input.isdigit() else 5
        
        platforms_input = input("Platforms (ebay,amazon or 'all' for both, default 'all'): ").strip().lower()
        if platforms_input == 'all' or not platforms_input:
            platforms = ["ebay", "amazon"]
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
        platforms = ["ebay", "amazon"]
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
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

