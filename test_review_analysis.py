"""
Test script for Review Analysis Agent
"""
import asyncio
import json
import logging
from agents import ReviewAnalysisAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_review_analysis():
    """Test the Review Analysis Agent."""
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("⚠️  config.json not found. Using default configuration.")
        config = {}
    
    # Initialize agent
    agent_config = config.get("agents", {}).get("review_analysis", {})
    agent = ReviewAnalysisAgent(agent_config)
    
    # Test 1: Basic review analysis
    print("\n" + "="*60)
    print("Test 1: Basic Review Analysis")
    print("="*60)
    
    sample_reviews = [
        {
            "text": "This product is amazing! Great quality and fast shipping. Highly recommend!",
            "author": "Customer1",
            "rating": 5
        },
        {
            "text": "Good value for money. Works as expected. Nothing special but decent.",
            "author": "Customer2",
            "rating": 4
        },
        {
            "text": "Terrible quality. Broke after a week. Very disappointed with this purchase.",
            "author": "Customer3",
            "rating": 2
        },
        {
            "text": "Excellent product! Love it! Best purchase I've made this year.",
            "author": "Customer4",
            "rating": 5
        },
        {
            "text": "It's okay, nothing special. The price is reasonable but could be better.",
            "author": "Customer5",
            "rating": 3
        }
    ]
    
    result = await agent.execute({
        "reviews": sample_reviews,
        "extract_themes": True
    })
    
    if result.get("success"):
        print(f"\n✅ Review analysis completed")
        
        sentiment_summary = result.get("sentiment_summary", {})
        print(f"\n📊 Sentiment Summary:")
        print(f"   Total Reviews: {sentiment_summary.get('total_reviews', 0)}")
        print(f"   Positive: {sentiment_summary.get('positive_count', 0)} ({sentiment_summary.get('positive_percent', 0)}%)")
        print(f"   Negative: {sentiment_summary.get('negative_count', 0)} ({sentiment_summary.get('negative_percent', 0)}%)")
        print(f"   Neutral: {sentiment_summary.get('neutral_count', 0)}")
        print(f"   Average Sentiment Score: {sentiment_summary.get('average_sentiment_score', 0):.3f}")
        print(f"   Overall Sentiment: {sentiment_summary.get('overall_sentiment', 'N/A')}")
        
        print(f"\n📝 Analyzed Reviews:")
        for i, review in enumerate(result.get("analyzed_reviews", [])[:3], 1):
            sentiment = review.get("sentiment", {})
            print(f"\n   {i}. {review.get('text', '')[:60]}...")
            print(f"      Sentiment: {sentiment.get('label', 'N/A')} (Score: {sentiment.get('score', 0):.3f})")
        
        themes = result.get("themes", [])
        if themes:
            print(f"\n🎯 Common Themes:")
            for theme in themes[:3]:
                print(f"\n   - {theme['theme'].capitalize()}:")
                print(f"     Total Mentions: {theme['total_mentions']}")
                print(f"     Positive: {theme['positive_mentions']} ({theme['positive_percent']:.1f}%)")
                print(f"     Negative: {theme['negative_mentions']} ({theme['negative_percent']:.1f}%)")
    else:
        print(f"\n❌ Review analysis failed: {result.get('error')}")
    
    # Test 2: Product reviews analysis
    print("\n" + "="*60)
    print("Test 2: Product Reviews Analysis")
    print("="*60)
    
    product_reviews = [
        {"text": "Great headphones! Sound quality is excellent and battery lasts long.", "rating": 5},
        {"text": "Good price but the build quality could be better. Sound is decent.", "rating": 4},
        {"text": "Amazing value! Works perfectly and shipping was super fast.", "rating": 5},
        {"text": "Not worth the money. Poor sound quality and uncomfortable to wear.", "rating": 2},
        {"text": "Decent product. Nothing special but it works fine for the price.", "rating": 3},
        {"text": "Love these! Best headphones I've ever owned. Highly recommend!", "rating": 5},
        {"text": "Terrible customer service. Product broke and they refused to help.", "rating": 1},
        {"text": "Good overall but the design could be improved. Sound is great though.", "rating": 4}
    ]
    
    result2 = await agent.execute({
        "reviews": product_reviews,
        "extract_themes": True
    })
    
    if result2.get("success"):
        sentiment_summary2 = result2.get("sentiment_summary", {})
        print(f"\n✅ Analysis completed for product reviews")
        print(f"   Overall Sentiment: {sentiment_summary2.get('overall_sentiment', 'N/A')}")
        print(f"   Positive: {sentiment_summary2.get('positive_percent', 0):.1f}%")
        print(f"   Negative: {sentiment_summary2.get('negative_percent', 0):.1f}%")
        
        themes2 = result2.get("themes", [])
        if themes2:
            print(f"\n   Top Themes:")
            for theme in themes2[:3]:
                print(f"   - {theme['theme']}: {theme['total_mentions']} mentions")

if __name__ == "__main__":
    print("🚀 Testing Review Analysis Agent\n")
    print("ℹ️  Note: HuggingFace API key optional - uses mock analysis if not provided\n")
    
    asyncio.run(test_review_analysis())

