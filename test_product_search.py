"""
Test script for Product Search API Agent
"""
import asyncio
import json
import logging
from agents import ProductSearchAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_product_search():
    """Test the Product Search Agent."""
    
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
    
    # Test 1: Basic search
    print("\n" + "="*60)
    print("Test 1: Basic Product Search")
    print("="*60)
    result = await agent.execute({
        "search_term": "wireless headphones",
        "max_results": 5,
        "platforms": ["ebay", "amazon"]
    })
    
    print(f"\n✅ Search completed: {result['success']}")
    print(f"📊 Total results: {result['total_results']}")
    print(f"🛒 Platforms searched: {', '.join(result['platforms_searched'])}")
    
    if result['products']:
        print("\n📦 Products found:")
        for i, product in enumerate(result['products'][:3], 1):
            print(f"\n{i}. {product['name']}")
            print(f"   Retailer: {product['retailer']}")
            print(f"   Price: ${product['price']:.2f}")
            print(f"   Shipping: ${product['shipping_cost']:.2f}")
            print(f"   Total: ${product['total_price']:.2f}")
            if product.get('rating'):
                print(f"   Rating: {product['rating']}/5.0 ({product.get('review_count', 0)} reviews)")
    
    # Test 2: Search with price filters
    print("\n" + "="*60)
    print("Test 2: Search with Price Filters")
    print("="*60)
    result2 = await agent.execute({
        "search_term": "laptop",
        "max_results": 3,
        "platforms": ["ebay", "amazon"],
        "filters": {
            "min_price": 300,
            "max_price": 800
        }
    })
    
    print(f"\n✅ Search completed: {result2['success']}")
    print(f"📊 Total results: {result2['total_results']}")
    
    if result2['products']:
        print("\n📦 Products within price range:")
        for i, product in enumerate(result2['products'], 1):
            print(f"{i}. {product['name']} - ${product['total_price']:.2f}")
    
    # Test 3: eBay only search
    print("\n" + "="*60)
    print("Test 3: eBay Only Search")
    print("="*60)
    result3 = await agent.execute({
        "search_term": "smartphone",
        "max_results": 3,
        "platforms": ["ebay"]
    })
    
    print(f"\n✅ Search completed: {result3['success']}")
    print(f"📊 Total results: {result3['total_results']}")
    print(f"🛒 Platforms searched: {', '.join(result3['platforms_searched'])}")
    
    if result3['products']:
        print("\n📦 eBay products:")
        for i, product in enumerate(result3['products'], 1):
            print(f"{i}. {product['name']} - ${product['total_price']:.2f} ({product['retailer']})")

if __name__ == "__main__":
    print("🚀 Testing Product Search API Agent\n")
    print("ℹ️  Note: eBay search requires App ID in config.json")
    print("ℹ️  Amazon search uses mock data for testing\n")
    
    asyncio.run(test_product_search())

