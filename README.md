# Agentic AI E-Commerce Assistant

A modular agent-based AI system that provides personalized product recommendations by integrating with external APIs.

## Project Structure

```
Lab2/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py              # Base class for all agents
│   └── product_search_agent.py   # Product search agent
├── config.json                    # Configuration file
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys in `config.json`:
```json
{
  "agents": {
    "product_search": {
      "api_keys": {
        "ebay": "YOUR_EBAY_APP_ID"
      }
    }
  }
}
```

## API Setup

### Quick Start (No Authentication Required!)
The system works out of the box with **FakeStore** and **DummyJSON** APIs - no API keys needed! These are the default platforms.

### Primary APIs (No Authentication)
- **FakeStore API**: `https://fakestoreapi.com/products` - Free, no authentication required
- **DummyJSON API**: `https://dummyjson.com/products/search` - Free, no authentication required
- **DummyJSON Reviews**: `https://dummyjson.com/products/{id}` - Fetches real product reviews (numeric IDs only)

### Optional Premium APIs
- **eBay API (Free)**: See `API_SETUP_GUIDE.md` for detailed instructions
- **Amazon PA-API 5.0**: See `AMAZON_PAAPI_SETUP.md` for detailed instructions (requires setup)

## Usage

### Product Search Agent

```python
import asyncio
from agents import ProductSearchAgent

async def main():
    # Load config
    import json
    with open('config.json') as f:
        config = json.load(f)
    
    # Initialize agent
    agent = ProductSearchAgent(config.get("agents", {}).get("product_search", {}))
    
    # Search for products (default: fakestore, dummyjson)
    result = await agent.execute({
        "search_term": "laptop",
        "max_results": 5,
        "platforms": ["fakestore", "dummyjson"],  # No API keys needed!
        "filters": {
            "min_price": 20,
            "max_price": 100
        }
    })
    
    print(f"Found {result['total_results']} products")
    for product in result['products']:
        print(f"- {product['name']}: ${product['total_price']}")

asyncio.run(main())
```

## Features

### Product Search Agent
- **FakeStore API Integration**: Free product search, no authentication required (default)
- **DummyJSON API Integration**: Free product search with reviews, no authentication required (default)
- **eBay Finding API Integration**: Real product search from eBay (optional, requires API key, 5,000 calls/day)
- **Amazon PA-API 5.0 Integration**: Real Amazon product search with AWS Signature V4 (optional, requires setup)
- **Price Filtering**: Filter products by price range
- **Concurrent Searches**: Search multiple platforms simultaneously
- **Error Handling**: Graceful error handling and logging
- **Automatic Fallback**: Uses real APIs when available, falls back gracefully

### Price Comparison Agent
- **Multi-Retailer Comparison**: Compare prices across different retailers
- **Best Deal Detection**: Automatically identifies the best price
- **Price History Tracking**: Tracks price changes over time (30-day history)
- **Savings Calculation**: Shows how much you save with the best deal
- **Price Trends**: Analyzes price trends (increasing/decreasing/stable)
- **Integration with Product Search**: Works seamlessly with ProductSearchAgent results
- **Google Shopping API**: Direct integration with Google Shopping for price comparison

### Review Analysis Agent
- **Review Fetching**: Automatically fetches real reviews from DummyJSON for numeric product IDs
- **HuggingFace API Integration**: Real sentiment analysis using state-of-the-art models (router endpoint)
- **Sentiment Classification**: POSITIVE, NEGATIVE, NEUTRAL with confidence scores
- **Theme Extraction**: Identifies common topics (quality, price, shipping, functionality, etc.)
- **Batch Processing**: Analyzes multiple reviews concurrently
- **Sentiment Summary**: Overall statistics and percentages
- **Automatic Fallback**: Uses mock analysis if API unavailable

## Completed Agents

**Product Search API Agent** - Search products from FakeStore, DummyJSON, eBay, and Amazon
**Price Comparison API Agent** - Compare prices across retailers and track history
**Review Analysis Agent** - Analyze reviews with HuggingFace sentiment analysis
**Recommendation Engine Agent** - Synthesize recommendations from all agents

### Recommendation Engine Agent
- **Multi-Factor Scoring**: Combines price, sentiment, rating, and review count
- **Budget-Aware Recommendations**: Prioritizes products within user budget
- **Personalized Ranking**: Customizable weights for different factors
- **Reason Generation**: Provides human-readable explanations for each recommendation
- **Full Workflow Integration**: Works seamlessly with all other agents

## Next Steps

- Centralized Workflow Manager
- FastAPI REST Endpoints
- Comprehensive Test Suite
- Optional UI (Streamlit/Gradio)

