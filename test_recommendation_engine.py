"""
Test script for Recommendation Engine Agent
Tests the full workflow: Search → Compare → Analyze → Recommend
"""
import asyncio
import json
import logging
from agents import (
    ProductSearchAgent,
    PriceComparisonAgent,
    ReviewAnalysisAgent,
    RecommendationEngineAgent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_full_workflow():
    """Test the complete recommendation workflow."""
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("⚠️  config.json not found. Using default configuration.")
        config = {}
    
    # Initialize all agents
    search_config = config.get("agents", {}).get("product_search", {})
    comparison_config = config.get("agents", {}).get("price_comparison", {})
    review_config = config.get("agents", {}).get("review_analysis", {})
    recommendation_config = config.get("agents", {}).get("recommendation_engine", {})
    
    search_agent = ProductSearchAgent(search_config)
    comparison_agent = PriceComparisonAgent(comparison_config)
    review_agent = ReviewAnalysisAgent(review_config)
    recommendation_agent = RecommendationEngineAgent(recommendation_config)
    
    # User preferences
    user_preferences = {
        "budget": 100,
        "min_rating": 4.0,
        "max_recommendations": 5
    }
    
    print("\n" + "="*60)
    print("🛍️  Complete Recommendation Workflow Test")
    print("="*60)
    print(f"\n👤 User Preferences:")
    print(f"   Budget: ${user_preferences['budget']:.2f}")
    print(f"   Min Rating: {user_preferences['min_rating']}/5.0")
    
    # Step 1: Search for products
    print("\n" + "-"*60)
    print("Step 1: Product Search")
    print("-"*60)
    search_term = "wireless headphones"
    search_result = await search_agent.execute({
        "search_term": search_term,
        "max_results": 10,
        "platforms": ["ebay", "amazon"],
        "filters": {
            "max_price": user_preferences["budget"]
        }
    })
    
    if not search_result.get("success") or not search_result.get("products"):
        print("❌ Product search failed or no products found")
        return
    
    products = search_result["products"]
    print(f"✅ Found {len(products)} products")
    
    # Step 2: Compare prices
    print("\n" + "-"*60)
    print("Step 2: Price Comparison")
    print("-"*60)
    comparison_result = await comparison_agent.execute({
        "product_name": search_term,
        "products": products,
        "include_history": False
    })
    
    price_comparisons = {}
    if comparison_result.get("success"):
        # Map price comparisons by product_id
        for comp in comparison_result.get("comparisons", []):
            product_id = comp.get("product_id", "")
            if product_id:
                price_comparisons[product_id] = comp
        print(f"✅ Compared prices across {len(price_comparisons)} retailers")
    
    # Step 3: Analyze reviews
    print("\n" + "-"*60)
    print("Step 3: Review Analysis")
    print("-"*60)
    
    # Generate mock reviews for products (in production, these come from product search)
    mock_reviews_by_product = {}
    for product in products:
        product_id = product.get("product_id", "")
        rating = product.get("rating", 4.0)
        
        # Generate reviews based on rating
        reviews = []
        if rating >= 4.5:
            reviews = [
                {"text": "Excellent product! Highly recommend!", "rating": 5},
                {"text": "Great quality and fast shipping. Love it!", "rating": 5},
                {"text": "Amazing value for money. Very satisfied!", "rating": 5},
                {"text": "Perfect! Exceeded my expectations.", "rating": 5},
                {"text": "Good product, works as expected.", "rating": 4}
            ]
        elif rating >= 4.0:
            reviews = [
                {"text": "Good product, worth the price.", "rating": 4},
                {"text": "Decent quality, works fine.", "rating": 4},
                {"text": "Nice product but could be better.", "rating": 3},
                {"text": "Satisfied with the purchase.", "rating": 4},
                {"text": "It's okay, nothing special.", "rating": 3}
            ]
        else:
            reviews = [
                {"text": "Not great quality, disappointed.", "rating": 2},
                {"text": "Poor build quality, broke quickly.", "rating": 2},
                {"text": "Not worth the money.", "rating": 2},
                {"text": "Terrible product, avoid this.", "rating": 1},
                {"text": "Very disappointed with this purchase.", "rating": 2}
            ]
        
        mock_reviews_by_product[product_id] = reviews
    
    # Analyze reviews for each product
    review_analyses = {}
    for product_id, reviews in mock_reviews_by_product.items():
        review_result = await review_agent.execute({
            "reviews": reviews,
            "extract_themes": True
        })
        
        if review_result.get("success"):
            review_analyses[product_id] = review_result
    
    print(f"✅ Analyzed reviews for {len(review_analyses)} products")
    
    # Step 4: Generate recommendations
    print("\n" + "-"*60)
    print("Step 4: Generate Recommendations")
    print("-"*60)
    
    recommendation_result = await recommendation_agent.execute({
        "products": products,
        "price_comparisons": price_comparisons,
        "review_analyses": review_analyses,
        "user_preferences": user_preferences,
        "max_recommendations": 5
    })
    
    if recommendation_result.get("success"):
        summary = recommendation_result.get("summary", {})
        recommendations = recommendation_result.get("recommendations", [])
        
        print(f"\n✅ Generated {summary.get('total_recommendations', 0)} recommendations")
        print(f"📊 Average Score: {summary.get('average_score', 0):.3f}")
        
        if "price_range" in summary:
            price_range = summary["price_range"]
            print(f"💰 Price Range: ${price_range['min']:.2f} - ${price_range['max']:.2f}")
        
        if "top_recommendation" in summary:
            top = summary["top_recommendation"]
            print(f"\n⭐ Top Recommendation:")
            print(f"   Product: {top.get('name', 'N/A')}")
            print(f"   Score: {top.get('score', 0):.3f}")
            print(f"   Reason: {top.get('reason', 'N/A')}")
        
        print(f"\n📋 All Recommendations:")
        print("="*60)
        for i, rec in enumerate(recommendations, 1):
            product = rec.get("product", {})
            print(f"\n{i}. {product.get('name', 'Unknown Product')}")
            print(f"   Retailer: {product.get('retailer', 'N/A')}")
            print(f"   Price: ${product.get('price', 0):.2f}")
            print(f"   Rating: {product.get('rating', 0):.1f}/5.0 ({product.get('review_count', 0)} reviews)")
            print(f"   Recommendation Score: {rec.get('score', 0):.3f}")
            print(f"   Reason: {rec.get('reason', 'N/A')}")
            
            if price_data := rec.get("price_data"):
                print(f"   💰 Best Price: ${price_data.get('total_cost', 0):.2f}")
            
            if review_data := rec.get("review_data"):
                sentiment_summary = review_data.get("sentiment_summary", {})
                overall = sentiment_summary.get("overall_sentiment", "N/A")
                print(f"   💬 Reviews: {overall} sentiment")
    else:
        print(f"\n❌ Recommendation generation failed: {recommendation_result.get('error')}")

if __name__ == "__main__":
    print("🚀 Testing Recommendation Engine Agent\n")
    print("ℹ️  This test runs the complete workflow:\n")
    print("   1. Search products")
    print("   2. Compare prices")
    print("   3. Analyze reviews")
    print("   4. Generate recommendations\n")
    
    asyncio.run(test_full_workflow())

