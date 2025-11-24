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
        print("Warning: config.json not found. Using default configuration.")
        config = {}
    
    # Initialize agent
    agent_config = config.get("agents", {}).get("product_search", {})
    agent = ProductSearchAgent(agent_config)
    
    # Test 1: Basic search with new APIs (default)
    print("\n" + "="*60)
    print("Test 1: Basic Product Search (FakeStore & DummyJSON)")
    print("="*60)
    result = await agent.execute({
        "search_term": "laptop",
        "max_results": 5
        # Uses default platforms: ["fakestore", "dummyjson"]
    })
    
    print(f"\nSearch completed: {result['success']}")
    print(f"Total results: {result['total_results']}")
    print(f"Platforms searched: {', '.join(result['platforms_searched'])}")
    
    if result['products']:
        print("\nProducts found:")
        for i, product in enumerate(result['products'][:3], 1):
            print(f"\n{i}. {product['name']}")
            print(f"   Retailer: {product['retailer']}")
            print(f"   Price: ${product['price']:.2f}")
            print(f"   Shipping: ${product['shipping_cost']:.2f}")
            print(f"   Total: ${product['total_price']:.2f}")
            if product.get('rating'):
                print(f"   Rating: {product['rating']}/5.0 ({product.get('review_count', 0)} reviews)")
    
    # Test 1b: FakeStore only
    print("\n" + "="*60)
    print("Test 1b: FakeStore Only Search")
    print("="*60)
    result_fakestore = await agent.execute({
        "search_term": "electronics",
        "max_results": 5,
        "platforms": ["fakestore"]
    })
    
    print(f"\nSearch completed: {result_fakestore['success']}")
    print(f"Total results: {result_fakestore['total_results']}")
    print(f"Platforms searched: {', '.join(result_fakestore['platforms_searched'])}")
    
    # Test 1c: DummyJSON only
    print("\n" + "="*60)
    print("Test 1c: DummyJSON Only Search")
    print("="*60)
    result_dummyjson = await agent.execute({
        "search_term": "phone",
        "max_results": 5,
        "platforms": ["dummyjson"]
    })
    
    print(f"\nSearch completed: {result_dummyjson['success']}")
    print(f"Total results: {result_dummyjson['total_results']}")
    print(f"Platforms searched: {', '.join(result_dummyjson['platforms_searched'])}")
    
    if result_dummyjson['products']:
        print("\nDummyJSON products:")
        for i, product in enumerate(result_dummyjson['products'][:3], 1):
            print(f"{i}. {product['name']} - ${product['total_price']:.2f}")
            if product.get('discount_percentage'):
                print(f"   Discount: {product['discount_percentage']}%")
    
    # Test 1d: Legacy APIs (eBay/Amazon)
    print("\n" + "="*60)
    print("Test 1d: Legacy APIs (eBay/Amazon)")
    print("="*60)
    result_legacy = await agent.execute({
        "search_term": "wireless headphones",
        "max_results": 5,
        "platforms": ["ebay", "amazon"]
    })
    
    print(f"\nSearch completed: {result_legacy['success']}")
    print(f"Total results: {result_legacy['total_results']}")
    print(f"Platforms searched: {', '.join(result_legacy['platforms_searched'])}")
    
    # Test 2: Search with price filters
    print("\n" + "="*60)
    print("Test 2: Search with Price Filters")
    print("="*60)
    result2 = await agent.execute({
        "search_term": "laptop",
        "max_results": 3,
        "platforms": ["fakestore", "dummyjson"],
        "filters": {
            "min_price": 10,
            "max_price": 100
        }
    })
    
    print(f"\nSearch completed: {result2['success']}")
    print(f"Total results: {result2['total_results']}")
    
    if result2['products']:
        print("\nProducts within price range:")
        for i, product in enumerate(result2['products'], 1):
            print(f"{i}. {product['name']} - ${product['total_price']:.2f}")
    
    # Test 3: All platforms combined
    print("\n" + "="*60)
    print("Test 3: All Platforms Combined")
    print("="*60)
    result3 = await agent.execute({
        "search_term": "smartphone",
        "max_results": 3,
        "platforms": ["fakestore", "dummyjson", "ebay", "amazon"]
    })
    
    print(f"\nSearch completed: {result3['success']}")
    print(f"Total results: {result3['total_results']}")
    print(f"Platforms searched: {', '.join(result3['platforms_searched'])}")
    
    if result3['products']:
        print("\nProducts from all platforms:")
        for i, product in enumerate(result3['products'], 1):
            print(f"{i}. {product['name']} - ${product['total_price']:.2f} ({product['retailer']})")

if __name__ == "__main__":
    print("Testing Product Search API Agent\n")
    print("Note: New APIs (FakeStore & DummyJSON) require no authentication")
    print("Note: Legacy APIs - eBay requires App ID, Amazon uses mock data\n")
    
    asyncio.run(test_product_search())

