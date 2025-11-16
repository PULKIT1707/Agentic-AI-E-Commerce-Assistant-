"""
Test script for Price Comparison API Agent
"""
import asyncio
import json
import logging
from agents import ProductSearchAgent, PriceComparisonAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_price_comparison():
    """Test the Price Comparison Agent."""
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("⚠️  config.json not found. Using default configuration.")
        config = {}
    
    # Initialize agents
    search_config = config.get("agents", {}).get("product_search", {})
    comparison_config = config.get("agents", {}).get("price_comparison", {})
    
    search_agent = ProductSearchAgent(search_config)
    comparison_agent = PriceComparisonAgent(comparison_config)
    
    # Test 1: Basic price comparison
    print("\n" + "="*60)
    print("Test 1: Basic Price Comparison")
    print("="*60)
    
    # First, search for products
    search_result = await search_agent.execute({
        "search_term": "wireless headphones",
        "max_results": 10,
        "platforms": ["ebay", "amazon"]
    })
    
    if search_result.get("success") and search_result.get("products"):
        products = search_result["products"]
        print(f"\n✅ Found {len(products)} products from search")
        
        # Now compare prices
        comparison_result = await comparison_agent.execute({
            "product_name": "wireless headphones",
            "products": products,
            "include_history": False,
            "use_google_shopping": False  # Set to True if you have Google API configured
        })
        
        if comparison_result.get("success"):
            print(f"\n✅ Price comparison completed")
            print(f"📊 Total retailers compared: {comparison_result.get('total_retailers', 0)}")
            
            best_deal = comparison_result.get("best_deal", {})
            print(f"\n💰 Best Deal:")
            print(f"   Retailer: {best_deal.get('retailer', 'N/A')}")
            print(f"   Total Cost: ${best_deal.get('total_cost', 0):.2f}")
            print(f"   Price: ${best_deal.get('price', 0):.2f}")
            print(f"   Shipping: ${best_deal.get('shipping_cost', 0):.2f}")
            print(f"   Savings: ${best_deal.get('savings', 0):.2f} ({best_deal.get('savings_percent', 0):.1f}%)")
            
            print(f"\n📋 All Comparisons:")
            for i, comp in enumerate(comparison_result.get("comparisons", []), 1):
                print(f"\n{i}. {comp['retailer']}")
                print(f"   Total: ${comp['total_cost']:.2f} (${comp['price']:.2f} + ${comp['shipping_cost']:.2f} shipping)")
                print(f"   Options: {comp.get('options_count', 0)}")
                if comp.get('rating'):
                    print(f"   Rating: {comp['rating']}/5.0 ({comp.get('review_count', 0)} reviews)")
        else:
            print(f"\n❌ Price comparison failed: {comparison_result.get('error')}")
    else:
        print(f"\n❌ Product search failed or no products found")
    
    # Test 2: Price comparison with history
    print("\n" + "="*60)
    print("Test 2: Price Comparison with History")
    print("="*60)
    
    search_result2 = await search_agent.execute({
        "search_term": "laptop",
        "max_results": 5,
        "platforms": ["amazon"]
    })
    
    if search_result2.get("success") and search_result2.get("products"):
        products2 = search_result2["products"]
        
        # First comparison
        comp_result1 = await comparison_agent.execute({
            "product_name": "laptop",
            "products": products2,
            "include_history": True
        })
        
        print(f"\n✅ First comparison completed")
        
        # Wait a bit and do second comparison to generate history
        await asyncio.sleep(1)
        
        comp_result2 = await comparison_agent.execute({
            "product_name": "laptop",
            "products": products2,
            "include_history": True
        })
        
        if comp_result2.get("success"):
            print(f"\n✅ Second comparison completed (with history)")
            
            for comp in comp_result2.get("comparisons", []):
                if "price_trend" in comp:
                    trend = comp["price_trend"]
                    print(f"\n{comp['retailer']}:")
                    print(f"   Trend: {trend.get('trend', 'N/A')}")
                    print(f"   Change: {trend.get('change_percent', 0):.2f}%")
                    print(f"   Data points: {trend.get('data_points', 0)}")

if __name__ == "__main__":
    print("🚀 Testing Price Comparison API Agent\n")
    print("ℹ️  This test uses ProductSearchAgent to get products, then compares prices\n")
    
    asyncio.run(test_price_comparison())

