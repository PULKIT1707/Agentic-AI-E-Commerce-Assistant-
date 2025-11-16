"""
Comprehensive Test Suite for Workflow Manager
Tests all required scenarios: budget constraints, specific requirements, comparative shopping
"""
import asyncio
import json
import logging
from agents import WorkflowManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def test_budget_constraints():
    """Test workflow with strict budget constraints."""
    print("\n" + "="*60)
    print("Test 1: Budget Constraints")
    print("="*60)
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("⚠️  config.json not found. Using default configuration.")
        config = {}
    
    workflow_manager = WorkflowManager(config)
    
    # Test with strict budget
    user_query = {
        "search_term": "wireless headphones",
        "max_results": 10,
        "platforms": ["ebay", "amazon"],
        "filters": {
            "max_price": 50  # Strict budget constraint
        },
        "user_preferences": {
            "budget": 50,
            "min_rating": 4.0,
            "max_recommendations": 5
        },
        "include_price_comparison": True,
        "include_review_analysis": True
    }
    
    print(f"\n💰 Budget: ${user_query['user_preferences']['budget']:.2f}")
    print(f"🔍 Search Term: '{user_query['search_term']}'")
    
    result = await workflow_manager.execute_workflow(user_query)
    
    if result["success"]:
        print(f"\n✅ Workflow completed successfully")
        print(f"📊 Total Products Found: {result['summary'].get('total_products_found', 0)}")
        print(f"⭐ Recommendations Generated: {len(result['recommendations'])}")
        
        if result["recommendations"]:
            print(f"\n📋 Top Recommendations (within budget):")
            for i, rec in enumerate(result["recommendations"][:3], 1):
                product = rec.get("product", {})
                price = product.get("price", 0)
                if price_data := rec.get("price_data"):
                    price = price_data.get("total_cost", price)
                
                print(f"\n{i}. {product.get('name', 'Unknown')}")
                print(f"   Price: ${price:.2f}")
                print(f"   Score: {rec.get('score', 0):.3f}")
                print(f"   Reason: {rec.get('reason', 'N/A')}")
                
                # Verify budget constraint
                if price > user_query["user_preferences"]["budget"]:
                    print(f"   ⚠️  WARNING: Price exceeds budget!")
        else:
            print("\n⚠️  No recommendations generated (may be due to budget constraints)")
    else:
        print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
    
    return result


async def test_specific_requirements():
    """Test workflow with specific product requirements."""
    print("\n" + "="*60)
    print("Test 2: Specific Requirements")
    print("="*60)
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("⚠️  config.json not found. Using default configuration.")
        config = {}
    
    workflow_manager = WorkflowManager(config)
    
    # Test with specific requirements
    user_query = {
        "search_term": "laptop computer",
        "max_results": 15,
        "platforms": ["ebay", "amazon"],
        "filters": {
            "min_price": 500,
            "max_price": 1500
        },
        "user_preferences": {
            "budget": 1500,
            "min_rating": 4.5,  # High rating requirement
            "max_recommendations": 5
        },
        "include_price_comparison": True,
        "include_review_analysis": True
    }
    
    print(f"\n📋 Requirements:")
    print(f"   Price Range: ${user_query['filters']['min_price']:.2f} - ${user_query['filters']['max_price']:.2f}")
    print(f"   Min Rating: {user_query['user_preferences']['min_rating']}/5.0")
    print(f"   Budget: ${user_query['user_preferences']['budget']:.2f}")
    print(f"🔍 Search Term: '{user_query['search_term']}'")
    
    result = await workflow_manager.execute_workflow(user_query)
    
    if result["success"]:
        print(f"\n✅ Workflow completed successfully")
        print(f"📊 Total Products Found: {result['summary'].get('total_products_found', 0)}")
        print(f"⭐ Recommendations Generated: {len(result['recommendations'])}")
        
        if result["recommendations"]:
            print(f"\n📋 Recommendations (meeting specific requirements):")
            for i, rec in enumerate(result["recommendations"], 1):
                product = rec.get("product", {})
                rating = product.get("rating", 0)
                price = product.get("price", 0)
                if price_data := rec.get("price_data"):
                    price = price_data.get("total_cost", price)
                
                print(f"\n{i}. {product.get('name', 'Unknown')}")
                print(f"   Price: ${price:.2f}")
                print(f"   Rating: {rating:.1f}/5.0")
                print(f"   Score: {rec.get('score', 0):.3f}")
                print(f"   Reason: {rec.get('reason', 'N/A')}")
                
                # Verify requirements
                meets_rating = rating >= user_query["user_preferences"]["min_rating"]
                meets_price = (price >= user_query["filters"]["min_price"] and 
                              price <= user_query["filters"]["max_price"])
                
                if not meets_rating:
                    print(f"   ⚠️  Rating below requirement")
                if not meets_price:
                    print(f"   ⚠️  Price outside range")
    else:
        print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
    
    return result


async def test_comparative_shopping():
    """Test workflow for comparative shopping across multiple products."""
    print("\n" + "="*60)
    print("Test 3: Comparative Shopping")
    print("="*60)
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("⚠️  config.json not found. Using default configuration.")
        config = {}
    
    workflow_manager = WorkflowManager(config)
    
    # Test comparative shopping
    user_query = {
        "search_term": "smartphone",
        "max_results": 20,  # More results for comparison
        "platforms": ["ebay", "amazon"],
        "filters": {
            "min_price": 200,
            "max_price": 800
        },
        "user_preferences": {
            "budget": 800,
            "min_rating": 4.0,
            "max_recommendations": 10  # More recommendations for comparison
        },
        "include_price_comparison": True,
        "include_review_analysis": True
    }
    
    print(f"\n🛒 Comparative Shopping Test")
    print(f"🔍 Search Term: '{user_query['search_term']}'")
    print(f"📊 Max Results: {user_query['max_results']}")
    print(f"💰 Price Range: ${user_query['filters']['min_price']:.2f} - ${user_query['filters']['max_price']:.2f}")
    
    result = await workflow_manager.execute_workflow(user_query)
    
    if result["success"]:
        print(f"\n✅ Workflow completed successfully")
        print(f"📊 Total Products Found: {result['summary'].get('total_products_found', 0)}")
        print(f"💰 Price Comparisons: {result['summary'].get('price_comparisons_count', 0)}")
        print(f"💬 Review Analyses: {result['summary'].get('review_analyses_count', 0)}")
        print(f"⭐ Recommendations Generated: {len(result['recommendations'])}")
        
        if result["recommendations"]:
            print(f"\n📊 Comparison Summary:")
            summary = result["summary"]
            if "price_range" in summary:
                price_range = summary["price_range"]
                print(f"   Price Range: ${price_range['min']:.2f} - ${price_range['max']:.2f}")
            print(f"   Average Score: {summary.get('average_score', 0):.3f}")
            
            if "top_recommendation" in summary:
                top = summary["top_recommendation"]
                print(f"\n⭐ Top Recommendation:")
                print(f"   Product: {top.get('name', 'N/A')}")
                print(f"   Score: {top.get('score', 0):.3f}")
                print(f"   Reason: {top.get('reason', 'N/A')}")
            
            print(f"\n📋 All Recommendations (Ranked):")
            print("-" * 60)
            for i, rec in enumerate(result["recommendations"], 1):
                product = rec.get("product", {})
                price = product.get("price", 0)
                if price_data := rec.get("price_data"):
                    price = price_data.get("total_cost", price)
                
                retailer = product.get("retailer", "Unknown")
                rating = product.get("rating", 0)
                review_count = product.get("review_count", 0)
                
                print(f"\n{i}. {product.get('name', 'Unknown')}")
                print(f"   Retailer: {retailer}")
                print(f"   Price: ${price:.2f}")
                print(f"   Rating: {rating:.1f}/5.0 ({review_count} reviews)")
                print(f"   Score: {rec.get('score', 0):.3f}")
                print(f"   Reason: {rec.get('reason', 'N/A')}")
                
                # Show price comparison if available
                if price_data := rec.get("price_data"):
                    best_deal = price_data.get("best_deal", {})
                    if best_deal.get("retailer") == retailer:
                        print(f"   💰 Best Deal Available!")
                
                # Show review sentiment if available
                if review_data := rec.get("review_data"):
                    sentiment_summary = review_data.get("sentiment_summary", {})
                    overall = sentiment_summary.get("overall_sentiment", "N/A")
                    positive_pct = sentiment_summary.get("positive_percent", 0)
                    print(f"   💬 Sentiment: {overall} ({positive_pct:.1f}% positive)")
    else:
        print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
    
    return result


async def test_workflow_steps():
    """Test individual workflow steps."""
    print("\n" + "="*60)
    print("Test 4: Individual Workflow Steps")
    print("="*60)
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("⚠️  config.json not found. Using default configuration.")
        config = {}
    
    workflow_manager = WorkflowManager(config)
    
    # Test Step 1: Search only
    print("\n--- Step 1: Product Search Only ---")
    search_result = await workflow_manager.search_products_only(
        search_term="tablet",
        max_results=5,
        platforms=["ebay", "amazon"]
    )
    
    if search_result.get("success"):
        print(f"✅ Found {search_result.get('total_results', 0)} products")
        products = search_result.get("products", [])
        if products:
            print(f"   Sample: {products[0].get('name', 'N/A')}")
    else:
        print(f"❌ Search failed: {search_result.get('error', 'Unknown error')}")
        return
    
    # Test Step 2: Price comparison only
    print("\n--- Step 2: Price Comparison Only ---")
    comparison_result = await workflow_manager.compare_prices_only(
        product_name="tablet",
        products=products[:3]  # Use first 3 products
    )
    
    if comparison_result.get("success"):
        comparisons = comparison_result.get("comparisons", [])
        print(f"✅ Compared prices for {len(comparisons)} products")
    else:
        print(f"⚠️  Price comparison: {comparison_result.get('error', 'Unknown error')}")
    
    # Test Step 3: Review analysis only
    print("\n--- Step 3: Review Analysis Only ---")
    mock_reviews = [
        {"text": "Great product! Highly recommend!", "rating": 5},
        {"text": "Good quality and fast shipping.", "rating": 4},
        {"text": "Works as expected.", "rating": 4}
    ]
    
    review_result = await workflow_manager.analyze_reviews_only(
        reviews=mock_reviews,
        extract_themes=True
    )
    
    if review_result.get("success"):
        sentiment_summary = review_result.get("sentiment_summary", {})
        print(f"✅ Review analysis completed")
        print(f"   Overall Sentiment: {sentiment_summary.get('overall_sentiment', 'N/A')}")
        print(f"   Positive: {sentiment_summary.get('positive_percent', 0):.1f}%")
    else:
        print(f"❌ Review analysis failed: {review_result.get('error', 'Unknown error')}")


async def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "="*60)
    print("🧪 Comprehensive Workflow Manager Test Suite")
    print("="*60)
    print("\nThis test suite validates:")
    print("  1. Budget constraints")
    print("  2. Specific requirements")
    print("  3. Comparative shopping")
    print("  4. Individual workflow steps")
    
    results = {}
    
    # Test 1: Budget Constraints
    results["budget_constraints"] = await test_budget_constraints()
    
    # Test 2: Specific Requirements
    results["specific_requirements"] = await test_specific_requirements()
    
    # Test 3: Comparative Shopping
    results["comparative_shopping"] = await test_comparative_shopping()
    
    # Test 4: Individual Steps
    await test_workflow_steps()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    success_count = sum(1 for r in results.values() if r.get("success"))
    total_count = len(results)
    
    print(f"\n✅ Successful Tests: {success_count}/{total_count}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("🚀 Starting Workflow Manager Test Suite\n")
    asyncio.run(run_all_tests())

